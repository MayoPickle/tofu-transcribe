import os
import json
from script.parse_srt import parse_srt
from script.emotion_analysis import (
    analyze_individual_sentences,
    group_and_average,
    group_by_individual_scores
)
from script.utils import extract_highest_groups
from script.plot import EmotionTrendPlotter
from speech.emotion_analysis import EmotionSRTProcessor


class EmotionAnalyzer:
    """Handles emotion analysis tasks like processing SRT files and saving results."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def analyze_emotions(self, srt_file, work_dir):
        """Perform emotion analysis on the SRT file."""
        self.logger.info(f"Starting emotion analysis for: {srt_file}")

        # Parse subtitles
        subtitles = parse_srt(srt_file)
        self.logger.info(f"Loaded {len(subtitles)} subtitles from SRT file.")

        # Perform individual emotion analysis
        individual_results = analyze_individual_sentences(
            subtitles=subtitles,
            model_name=self.config["emotion_model"]
        )

        # Save individual results to JSON
        self._save_individual_results(individual_results, work_dir)

        # Perform group emotion analysis
        grouped_ind = group_by_individual_scores(individual_results, group_size=64, step=4)
        grouped_comb = group_and_average(
            subtitles=subtitles, group_size=64, step=4,
            model_name=self.config["emotion_model"], max_length=512
        )

        # Extract highest emotion groups
        highest_results = {
            "individual": extract_highest_groups(*grouped_ind[:3]),
            "combined": extract_highest_groups(*grouped_comb[:3])
        }

        # Save results and generate plots
        self._save_results(highest_results, work_dir)
        self._plot_emotion_trends(grouped_comb, work_dir)

    def _save_individual_results(self, individual_results, work_dir):
        """Save individual emotion results to a JSON file."""
        output_json = os.path.join(work_dir, "individual_emotion_results.json")
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(individual_results, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Individual emotion results saved to: {output_json}")

    def _save_results(self, highest_results, work_dir):
        """Save the highest emotion groups to a JSON file."""
        output_json = os.path.join(work_dir, "emotion_highest.json")
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(highest_results, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Emotion analysis results saved to: {output_json}")

    def _plot_emotion_trends(self, grouped_comb, work_dir):
        """Plot and save emotion trends."""
        plot_file = os.path.join(work_dir, "emotion_trends.png")

        # Extract times and scores for plotting
        times = grouped_comb[0]  # Time intervals
        scores = grouped_comb[1]  # Emotion scores

        # Simplified plot: Times and scores only
        EmotionTrendPlotter.plot_emotion_trends(
            times=times,
            scores=scores,
            labels=None,  # No labels needed
            positive_group=None,  # Not used
            negative_group=None,  # Not used
            output_file=plot_file,
        )
        self.logger.info(f"Emotion trend plot saved to: {plot_file}")

    def process_speech_emotions(self, work_dir):
        """Perform speech emotion analysis and save SRT with emotion scores."""
        speech_analyzer = EmotionSRTProcessor(work_dir=work_dir)
        speech_analyzer.process_and_save()
