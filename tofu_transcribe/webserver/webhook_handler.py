from flask import Flask, request, jsonify
import os
from concurrent.futures import ThreadPoolExecutor
from utils.evaluation_handler import EvaluationHandler
from nlp.nlp_emotion_analyzer import NLPAnalyzer
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

    def _process_video(self, full_path, event_data):
        """Process the video and perform all required operations."""
        try:
            work_dir = self.video_processor.prepare_work_dir(full_path)
            self._convert_video_to_audio(full_path, work_dir)
            self._process_transcription(work_dir)
            clickbait_title = self._analyze_emotions_and_generate_title(work_dir)

            print(clickbait_title)

            if self.config["server_chan_key"]:
                self._evaluate_and_notify(work_dir, event_data, clickbait_title)
        except Exception as e:
            self.logger.error(f"Error processing video file {full_path}: {e}")
        finally:
            self._remove_active_task(full_path)

    def _convert_video_to_audio(self, full_path, work_dir):
        """Convert video to WAV format."""
        wav_file = os.path.join(work_dir, "tofu_transcribe.wav")
        self.video_processor.convert_to_wav(full_path, wav_file)

    def _process_transcription(self, work_dir):
        """Run transcription and check for SRT file."""
        self.video_processor.run_whisper(os.path.join(work_dir, "tofu_transcribe.wav"), work_dir)

    def _analyze_emotions_and_generate_title(self, work_dir):
        """Analyze emotions and generate a clickbait title if applicable."""
        srt_file = self.video_processor.find_srt_file(work_dir)
        if not srt_file:
            self.logger.error(f"No SRT file found in {work_dir}. Skipping emotion analysis.")
            return None

        self.emotion_analyzer.process_speech_emotions(work_dir)
        self.emotion_analyzer.analyze_emotions(srt_file, work_dir)

        if self.config["open_ai_key"]:
            nlp_handler = NLPAnalyzer(api_key=self.config["open_ai_key"], model=self.config["nlp_model"])
            return nlp_handler.generate_clickbait_title(work_dir=work_dir)
        return None

    def _evaluate_and_notify(self, work_dir, event_data, clickbait_title=None):
        """Handle evaluation and send notifications."""
        evaluation_handler = EvaluationHandler(
            work_dir=work_dir,
            send_key=self.config["server_chan_key"],
            event_data=event_data,
            clickbait_title=clickbait_title,
        )
        evaluation_handler.evaluate_and_notify()

    def _remove_active_task(self, full_path):
        """Safely remove a task from the active task set."""
        with self.task_lock:
            self.active_tasks.discard(full_path)

    def _tofu_transcribe_handler(self):
        """Handle incoming webhook requests."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        # Validate and extract data
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

        # Avoid duplicate tasks
        with self.task_lock:
            if full_path in self.active_tasks:
                self.logger.warning(f"Task for {full_path} is already running.")
                return jsonify({"message": "Task already running", "file": relative_path}), 200
            self.active_tasks.add(full_path)

        # Submit task for processing
        self.executor.submit(self._process_video, full_path, event_data)
        return jsonify({"message": "Task started", "file": relative_path}), 200

    def run(self):
        """Start the web server."""
        self.logger.info("Starting production webserver with Waitress...")
        serve(self.app, host=self.config["flask_host"], port=self.config["flask_port"])
