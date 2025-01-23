import os
import json
from webserver.serverchan_service import ServerChanPush

class EvaluationHandler:
    """
    Evaluation Handler that checks weighted_score_rank.json for high scores
    and sends a notification if the score exceeds a threshold.
    """

    def __init__(self, work_dir, send_key, event_data, score_threshold=0.78):
        """
        Initialize the EvaluationHandler.

        :param work_dir: The directory containing weighted_score_rank.json
        :param send_key: The ServerChan SendKey for push notifications
        :param score_threshold: The score threshold for triggering a notification
        """
        self.work_dir = work_dir
        self.file_name = "weighted_score_rank.json"
        self.file_path = os.path.join(work_dir, self.file_name)
        self.server_push = ServerChanPush(send_key)
        self.score_threshold = score_threshold
        self.event_data = event_data

    def read_score_file(self):
        """
        Read and parse the weighted_score_rank.json file.

        :return: Parsed JSON data
        """
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Failed to parse JSON in {self.file_path}")
            return None

    def evaluate_and_notify(self):
        """
        Evaluate scores from the file and send a notification if criteria are met.
        """
        data = self.read_score_file()
        if not data:
            return

        # Process JSON array
        for entry in data:
            group_index = entry.get("group_index", "Unknown")
            weighted_score = entry.get("weighted_score", 0)
            content = entry.get("combined_text", "Not Available")

            if weighted_score > self.score_threshold:
                title = f"High Weighted Score Alert for Group {group_index}"
                content = (
                    f"The weighted score for Group {group_index} is {weighted_score:.2f}, exceeding the threshold of {self.score_threshold:.2f}.\n"
                    f"Room ID: {self.event_data.get("RoomId", "Unknown")}\n"
                    f"Name: {self.event_data.get("Name", "Unknown")}\n"
                    f"Title: {self.event_data.get("Title", "Unknown")}\n"
                    f"Content: {content}\n"
                    f"Time Range: {entry.get("time_range", "Not Available")}"
                )
                response = self.server_push.send(title, content)
                print(f"Notification sent for Group {group_index}:", response)
                break