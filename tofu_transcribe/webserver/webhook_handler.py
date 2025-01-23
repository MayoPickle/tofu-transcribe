from flask import Flask, request, jsonify
import os
from concurrent.futures import ThreadPoolExecutor
from utils.evaluation_handler import EvaluationHandler
from threading import Lock
from waitress import serve


class WebhookHandler:
    """Handles incoming webhooks for video processing."""

    def __init__(self, video_processor, emotion_analyzer, config, logger):
        """
        Initialize the webhook handler.
        :param video_processor: VideoProcessor instance
        :param emotion_analyzer: EmotionAnalyzer instance
        :param config: Configuration dictionary
        :param logger: Logger instance
        """
        self.video_processor = video_processor
        self.emotion_analyzer = emotion_analyzer
        self.config = config
        self.logger = logger
        self.app = Flask(__name__)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.active_tasks = set()
        self.task_lock = Lock()
        self._setup_routes()

    def _setup_routes(self):
        """Define Flask routes."""
        self.app.add_url_rule(
            "/v1/video2script",
            methods=["POST"],
            view_func=self._tofu_transcribe_handler,
        )

    def _process_task(self, full_path, event_data):
        """Process a video file in the background."""
        try:
            work_dir = self.video_processor.prepare_work_dir(full_path)
            wav_file = os.path.join(work_dir, "tofu_transcribe.wav")
            self.video_processor.convert_to_wav(full_path, wav_file)
            self.video_processor.run_whisper(wav_file, work_dir)

            srt_file = self.video_processor.find_srt_file(work_dir)
            if srt_file:
                self.emotion_analyzer.process_speech_emotions(work_dir)
                self.emotion_analyzer.analyze_emotions(srt_file, work_dir)
                self.logger.info(f"Processing completed. Results saved in: {work_dir}")
            else:
                self.logger.error(f"No SRT file found in {work_dir}. Skipping emotion analysis.")

            if self.config["server_chan_key"]:
                evaluation_handler = EvaluationHandler(work_dir=work_dir, send_key=self.config["server_chan_key"], event_data=event_data)
                evaluation_handler.evaluate_and_notify()
        except Exception as e:
            self.logger.error(f"Error processing video file {full_path}: {e}")
        finally:
            with self.task_lock:
                self.active_tasks.remove(full_path)

    def _tofu_transcribe_handler(self):
        """Handle incoming webhook requests."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        # Extract and validate request data
        try:
            event_type = data["EventType"]
            event_data = data["EventData"]
            relative_path = event_data["RelativePath"]
        except KeyError:
            return jsonify({"error": "Missing required fields"}), 400

        if event_type != "FileClosed":
            return jsonify({"message": f"Event type {event_type} ignored"}), 200

        full_path = os.path.join(self.config["live_root_dir"], relative_path)
        if not os.path.exists(full_path):
            self.logger.error(f"File not found: {full_path}")
            return jsonify({"error": f"File not found: {full_path}"}), 404

        # Avoid duplicate tasks for the same file
        with self.task_lock:
            if full_path in self.active_tasks:
                self.logger.warning(f"Task for {full_path} is already running.")
                return jsonify({"message": "Task already running", "file": relative_path}), 200
            self.active_tasks.add(full_path)

        # Submit background task
        self.executor.submit(self._process_task, full_path, event_data)
        return jsonify({"message": "Task started", "file": relative_path}), 200

    def run(self):
        """Start the web server."""
        self.logger.info("Starting production webserver with Waitress...")
        serve(self.app, host=self.config["flask_host"], port=self.config["flask_port"])
