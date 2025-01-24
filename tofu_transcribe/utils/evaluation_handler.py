import os
import json


class EvaluationHandler:
    """
    Evaluation Handler that checks weighted_score_rank.json for scores
    and saves all notifications locally regardless of score threshold.
    """

    def __init__(self, work_dir, event_data, clickbait_title="", score_threshold=0.86):
        """
        Initialize the EvaluationHandler.

        :param work_dir: The directory containing weighted_score_rank.json
        :param score_threshold: The score threshold for triggering a notification
        """
        self.clickbait_title = clickbait_title
        self.work_dir = work_dir
        self.file_name = "weighted_score_rank.json"
        self.file_path = os.path.join(work_dir, self.file_name)
        self.output_file = os.path.join(work_dir, "notifications_log.json")
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

    def save_notification_locally(self, notifications):
        """
        Save notifications to a local file.

        :param notifications: A list of notification entries
        """
        try:
            with open(self.output_file, 'w') as file:
                json.dump(notifications, file, indent=4)
            print(f"Notifications saved to {self.output_file}")
        except Exception as e:
            print(f"Error saving notifications: {e}")

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
            combined_text = entry.get("combined_text", "Not Available")
            time_range = entry.get("time_range", {})
            start_time = time_range.get("start", "Unknown")
            end_time = time_range.get("end", "Unknown")

            if weighted_score > self.score_threshold:
                title = f"High Score Alert: {self.event_data.get("Name", "Unknown")}"
                content = (
                    f"### High Score Alert\n\n"
                    f"**Group Index:** {group_index}\n"
                    f"**Weighted Score:** {weighted_score:.2f} (Threshold: {self.score_threshold:.2f})\n"
                    f"**Time Range:** {start_time} - {end_time}\n"
                    f"**Room ID:** {self.event_data.get("RoomId", "Unknown")}\n"
                    f"**Name:** {self.event_data.get("Name", "Unknown")}\n"
                    f"**Title:** {self.event_data.get("Title", "Unknown")}\n\n"
                    f"**Clickbait Title:** {self.clickbait_title}\n\n"
                    f"**Content:**\n{combined_text}\n"
                )
                response = self.server_push.send(title, content)
                print(f"Notification sent for Group {group_index}:", response)
                break

    def evaluate_and_notify(self):
        """
        Evaluate scores from the file and save all notifications locally.
        """
        data = self.read_score_file()
        if not data:
            return

        # Process JSON array
        entry = data[0]
        group_index = entry.get("group_index", "Unknown")
        weighted_score = entry.get("weighted_score", 0)
        combined_text = entry.get("combined_text", "Not Available")
        time_range = entry.get("time_range", {})
        start_time = time_range.get("start", "Unknown")
        end_time = time_range.get("end", "Unknown")

        if weighted_score > self.score_threshold:
            title = f"High Score Alert: {self.event_data.get("Name", "Unknown")}"
            content = (
                f"### High Score Alert\n\n"
                f"**Group Index:** {group_index}\n"
                f"**Weighted Score:** {weighted_score:.2f} (Threshold: {self.score_threshold:.2f})\n"
                f"**Time Range:** {start_time} - {end_time}\n"
                f"**Room ID:** {self.event_data.get("RoomId", "Unknown")}\n"
                f"**Name:** {self.event_data.get("Name", "Unknown")}\n"
                f"**Title:** {self.event_data.get("Title", "Unknown")}\n\n"
                f"**Clickbait Title:** {self.clickbait_title}\n\n"
                f"**Content:**\n{combined_text}\n"
            )
            response = self.server_push.send(title, content)
            print(f"Notification sent for Group {group_index}:", response)

        notifications = content

        self.save_notification_locally(notifications)
