import os
import json

from script.parse_srt import parse_srt
from TofuTranscribe.tofu_transcribe.script.script_emotion_analyzer import ScriptEmotionAnalyzer
from script.plot import EmotionTrendPlotter
from TofuTranscribe.tofu_transcribe.speech.speech_emotion_analyzer import SpeechEmotionAnalyzer


class EmotionAnalyzer:
    """Handles emotion analysis tasks like processing SRT files and saving results."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        # Initialize ScriptEmotionAnalyzer instance during initialization to avoid repeated model loading
        self.script_analyzer = ScriptEmotionAnalyzer(
            model_name=self.config["emotion_model"]
        )

    @staticmethod
    def _calculate_totle_score(work_dir):
        """Calculate the total score of the individual emotion results."""
        # Load grouped emotion results
        with open(os.path.join(work_dir, "grouped_emotion_results.json"), "r", encoding="utf-8") as f:
            grouped_emotion_results = json.load(f)

        # Load speech emotion analysis results
        with open(os.path.join(work_dir, "emotion_analysis_results.json"), "r", encoding="utf-8") as f:
            emotion_analysis_results = json.load(f)

        # Load individual emotion results
        with open(os.path.join(work_dir, "individual_emotion_results.json"), "r", encoding="utf-8") as f:
            individual_results = json.load(f)

        index_speech = 0
        index_individual = 0

        for result in grouped_emotion_results:
            group_size = result["group_size"]
            step = result["step"]

            # Calculate speech emotion score
            grouped_manbers = emotion_analysis_results[index_speech:index_speech + group_size]
            if len(grouped_manbers) > 0:
                result["speech_emotion_score"] = sum(
                    [grouped_manber["score"] for grouped_manber in grouped_manbers]
                ) / len(grouped_manbers)
            else:
                result["speech_emotion_score"] = 0
            index_speech += step

            # Calculate individual emotion score
            individual_manbers = individual_results[index_individual:index_individual + group_size]
            if len(individual_manbers) > 0:
                result["individual_emotion_score"] = sum(
                    [individual_manber["score"] for individual_manber in individual_manbers]
                ) / len(individual_manbers)
            else:
                result["individual_emotion_score"] = 0
            index_individual += step

            # Calculate weighted score
            result["weighted_score"] = (
                result["speech_emotion_score"] * 0.7
                + result["individual_emotion_score"] * 0.15
                + result["score"] * 0.15
            )

        # Save total scores
        output_path = os.path.join(work_dir, "totle_score.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(grouped_emotion_results, f, ensure_ascii=False, indent=4)

        return grouped_emotion_results

    def analyze_emotions(self, srt_file, work_dir):
        """Perform emotion analysis on the SRT file."""
        self.logger.info(f"Starting emotion analysis for: {srt_file}")

        # Parse subtitles
        subtitles = parse_srt(srt_file)
        self.logger.info(f"Loaded {len(subtitles)} subtitles from SRT file.")

        # Perform individual emotion analysis
        # Use self.script_analyzer.analyze_individual_sentences instead of the previous function
        individual_results = self.script_analyzer.analyze_individual_sentences(subtitles)

        # Save individual results to JSON
        self._save_individual_results(individual_results, work_dir)

        # Perform group emotion analysis
        # 1) Group based on individual scores
        self.script_analyzer.group_by_individual_scores(
            individual_results,
            group_size=64,
            step=4
        )

        # 2) Perform sliding window grouping and averaging
        self.script_analyzer.group_and_average(
            subtitles=subtitles,
            group_size=64,
            step=4,
            max_length=512,
            output_json_path=os.path.join(work_dir, "grouped_emotion_results.json")
        )

        # Calculate total scores
        groups_totle_scores = self._calculate_totle_score(work_dir)

        # Sort and retrieve top 3 groups by weighted score
        sorted_scores = sorted(
            groups_totle_scores,
            key=lambda x: x["weighted_score"],
            reverse=True
        )

        # Save results and generate plots
        self._save_results(sorted_scores[:3], work_dir)
        self._plot_emotion_trends(groups_totle_scores, work_dir)

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

    def _plot_emotion_trends(self, groups_totle_scores, work_dir):
        """Plot and save emotion trends."""
        plot_file = os.path.join(work_dir, "emotion_trends.png")

        # Extract times and scores for plotting
        times = [
            (group["time_range"]["start"], group["time_range"]["end"])
            for group in groups_totle_scores
        ]

        scores = [group["weighted_score"] for group in groups_totle_scores]

        # Simplified plot: Times and scores only
        EmotionTrendPlotter.plot_emotion_trends(
            times=times,
            scores=scores,
            labels=None,
            positive_group=None,
            negative_group=None,
            output_file=plot_file,
        )
        self.logger.info(f"Emotion trend plot saved to: {plot_file}")

    def process_speech_emotions(self, work_dir):
        """Perform speech emotion analysis and save SRT with emotion scores."""
        speech_analyzer = SpeechEmotionAnalyzer(work_dir=work_dir)
        speech_analyzer.process_and_save()
