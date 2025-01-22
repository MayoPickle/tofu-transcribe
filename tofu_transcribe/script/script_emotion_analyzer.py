import json
from transformers import pipeline
from tqdm import tqdm

class ScriptEmotionAnalyzer:
    """
    Encapsulates methods for single-sentence emotion analysis, group emotion analysis, etc.,
    to centralize the model and inference logic.
    """

    def __init__(self, model_name):
        """
        Initializes the sentiment-analysis pipeline to avoid repeated instantiation.
        :param model_name: The name of the model used for emotion analysis
        """
        self.model_name = model_name
        self.classifier = pipeline("sentiment-analysis", model=self.model_name, tokenizer=self.model_name)

    def analyze_individual_sentences(self, subtitles):
        """
        Perform emotion analysis for each subtitle individually.
        :param subtitles: List[Tuple[float, float, str]]
            Example: [(start_time, end_time, text), (1.0, 2.0, "subtitle text"), ...]
        :return: List[Dict[str, Any]]
            Emotion analysis results for each subtitle,
            e.g., [{"start": float, "end": float, "text": str, "label": str, "score": float}, ...]
        """
        individual_results = []

        for start, end, text in tqdm(subtitles, desc="Analyzing individual sentences"):
            emotion = self.classifier(text)[0]  # Analyze single sentence
            individual_results.append({
                "start": start,
                "end": end,
                "text": text,
                "label": emotion['label'],
                "score": emotion['score']
            })

        return individual_results

    def group_and_average(
        self,
        subtitles,
        group_size=32,
        step=2,
        max_length=512,
        output_json_path="grouped_emotion_results.json"
    ):
        """
        Group subtitles using a sliding window, perform emotion analysis for each group,
        and save the analysis results to a JSON file.
        :param subtitles: List[Tuple[float, float, str]]
        :param group_size: Number of subtitles per group
        :param step: Sliding window step size
        :param max_length: Maximum text length; trims the last sentence if it exceeds this length
        :param output_json_path: Path to save grouped results in JSON format
        :return: (grouped_times, grouped_scores, group_texts, group_labels)
        """
        grouped_scores = []
        grouped_times = []
        group_texts = []
        group_labels = []
        results = []  # To store results for JSON output

        for i in tqdm(range(0, len(subtitles) - group_size + 1, step), desc="Processing grouped subtitles"):
            group = subtitles[i:i + group_size]

            # Combine subtitles into a single text; trim last sentence if too long
            combined_text = " ".join(text for _, _, text in group)
            while len(combined_text) > max_length and len(group) > 1:
                group = group[:-1]
                combined_text = " ".join(text for _, _, text in group)

            # Skip group if single subtitle still exceeds max length
            if len(combined_text) > max_length:
                continue

            # Calculate average time for the group (optional, not necessarily used later)
            avg_time = sum((start + end) / 2 for start, end, _ in group) / len(group)

            # Perform emotion analysis for the combined text
            emotion = self.classifier(combined_text)[0]

            grouped_scores.append(emotion['score'])
            grouped_times.append((group[0][0], group[-1][1]))
            group_texts.append(combined_text)
            group_labels.append(emotion['label'])

            # Add group results to the list for JSON output
            results.append({
                "group_index": len(grouped_scores),
                "group_size": len(group),
                "step": step,
                "time_range": {
                    "start": group[0][0],
                    "end": group[-1][1]
                },
                "average_time": avg_time,
                "combined_text": combined_text,
                "label": emotion['label'],
                "score": emotion['score']
            })

        with open(output_json_path, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        return grouped_times, grouped_scores, group_texts, group_labels

    def group_by_individual_scores(self, individual_results, group_size=32, step=2):
        """
        Group based on individual emotion analysis results.
        :param individual_results: Output of analyze_individual_sentences()
        :param group_size: Number of results per group
        :param step: Sliding window step size
        :return: (grouped_times, grouped_scores, grouped_texts)
        """
        grouped_scores = []
        grouped_times = []
        grouped_texts = []

        for i in tqdm(range(0, len(individual_results) - group_size + 1, step), desc="Processing individual scores"):
            group = individual_results[i:i + group_size]

            # Simply average the scores; you can replace this with another weighting or calculation method
            group_score = sum(result['score'] for result in group) / group_size
            group_start = group[0]['start']
            group_end = group[-1]['end']
            group_text = " ".join(result['text'] for result in group)

            grouped_scores.append(group_score)
            grouped_times.append((group_start, group_end))
            grouped_texts.append(group_text)

        return grouped_times, grouped_scores, grouped_texts
