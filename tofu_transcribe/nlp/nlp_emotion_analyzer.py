import openai

class NLPAnalyzer:
    def __init__(self, api_key, model="gpt-4o-mini"):
        """
        Initialize the NLP Analyzer
        :param api_key: OpenAI API key
        :param model: The GPT model to use (default: gpt-4o-mini)
        """
        openai.api_key = api_key
        self.model = model

    def generate_clickbait_title(self, subtitle_file, max_length=10):
        """
        Generate a click-worthy title from a subtitle file
        :param subtitle_file: Path to the subtitle file (.srt or .txt)
        :param max_length: Maximum length of the title in characters
        :return: Generated title
        """
        try:
            # Read the subtitle file
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Define the prompt for OpenAI API
            prompt = (
                "Here is the content of a subtitle file. Please summarize it into an engaging video title "
                f"that is no more than {max_length} characters:\n\n"
                f"{content}\n\nTitle:"
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
