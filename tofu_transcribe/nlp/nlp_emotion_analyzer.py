import os
import json
import openai

class NLPAnalyzer:
    def __init__(self, api_key, model="gpt-4o-mini"):
        """
        Initialize the NLP Analyzer
        :param api_key: OpenAI API key
        :param model: The GPT model to use (default: gpt-4o-mini)
        """
        self.file_name = "weighted_score_rank.json"
        openai.api_key = api_key
        self.model = model

    
    def read_score_file(self, file_path):
        """
        Read and parse the weighted_score_rank.json file.

        :return: Parsed JSON data
        """
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Failed to parse JSON in {file_path}")
            return None

    def generate_clickbait_title(self, work_dir, max_length=10):
        """
        Generate a click-worthy title from a subtitle file
        :param work_dir: Path to the subtitle file (.json)
        :param max_length: Maximum length of the title in characters
        :return: Generated title
        """
        try:
            file_path = os.path.join(work_dir, self.file_name)
            # Read the subtitle file    
            data = self.read_score_file(file_path)

            # Define the prompt for OpenAI API
            prompt = (
                "Here is the content of a subtitle file. Please summarize it into an engaging video title "
                f"that is no more than {max_length} characters:\n\n"
                f"{data[0]['combined_text']}\n\nTitle:"
            )

            # Call the OpenAI GPT model to generate a title
            response = openai.Completion.create(
                model=self.model,
                prompt=prompt,
                max_tokens=50,
                temperature=0.7
            )

            # Extract and return the title
            title = response.choices[0].text.strip()
            return title if len(title) <= max_length else title[:max_length]

        except Exception as e:
            return f"Error generating title: {e}"
