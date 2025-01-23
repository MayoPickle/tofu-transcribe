import requests

class ServerChanPush:
    """
    ServerChan Push Service Class
    """

    def __init__(self, send_key):
        """
        Initialize the ServerChan Push Service
        :param send_key: SendKey provided by ServerChan
        """
        self.send_key = send_key
        self.api_url = f"https://sctapi.ftqq.com/{send_key}.send"

    def send(self, title, content):
        """
        Send a push notification
        :param title: Title of the push notification
        :param content: Content of the push notification (supports Markdown format)
        :return: Response result (JSON format)
        """
        data = {
            "title": title,
            "desp": content
        }
        try:
            response = requests.post(self.api_url, data=data)
            response.raise_for_status()  # Check if the HTTP request was successful
            return response.json()      # Return the response as JSON
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def test_push(self):
        """
        Test the push notification service
        :return: Response result of the test push
        """
        return self.send("Test Push", "This is a test message to verify the ServerChan push service.")
