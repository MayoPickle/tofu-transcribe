import os
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from waitress import serve

class WebhookHandler:
    def __init__(self, processor, config, logger):
        self.processor = processor
        self.config = config
        self.logger = logger
        self.app = Flask(__name__)
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.active_tasks = set()
        self.task_lock = Lock()
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule("/v1/video2script", methods=["POST"], view_func=self.video2script_handler)

    def background_task(self, full_path):
        try:
            self.processor.process_video(full_path)
        except Exception as e:
            self.logger.error(f"Error processing video file {full_path}: {e}")
        finally:
            with self.task_lock:
                self.active_tasks.remove(full_path)

    def video2script_handler(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

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

        with self.task_lock:
            if full_path in self.active_tasks:
                self.logger.warning(f"Task for {full_path} is already running.")
                return jsonify({"message": "Task already running", "file": relative_path}), 200

            self.active_tasks.add(full_path)

        self.executor.submit(self.background_task, full_path)
        return jsonify({"message": "Task started", "file": relative_path}), 200
    
    def run(self):
        self.logger.info("Starting production webserver with Waitress...")
        serve(self.app, host=self.config["flask_host"], port=self.config["flask_port"])
