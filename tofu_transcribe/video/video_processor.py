import os
import json
import glob
import subprocess
from script.parse_srt import parse_srt
from script.emotion_analysis import analyze_individual_sentences, group_and_average, group_by_individual_scores
from script.utils import extract_highest_groups
from script.plot import plot_emotion_trends

class VideoProcessor:
    """Class to handle video and emotion processing."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def convert_to_wav(self, input_file, output_wav):
        if os.path.exists(output_wav):
            self.logger.warning(f"Output WAV file already exists. Overwriting: {output_wav}")
            os.remove(output_wav)

        command = [
            "ffmpeg", "-i", input_file,
            "-ar", str(self.config["ffmpeg_options"]["sample_rate"]),
            "-ac", str(self.config["ffmpeg_options"]["channels"]),
            output_wav
        ]
        try:
            subprocess.run(command, check=True)
            self.logger.info(f"Converted to WAV: {output_wav}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error during conversion: {e}")
            raise

    def run_whisper(self, file_path, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        for ext in ["srt", "json", "txt"]:
            output_file = os.path.join(output_dir, f"transcription.{ext}")
            if os.path.exists(output_file):
                self.logger.warning(f"Output file already exists. Overwriting: {output_file}")
                os.remove(output_file)

        command = [
            "whisper",
            file_path,
            "--model", self.config["model"],
            "--device", self.config["device"],
            "--output_dir", output_dir,
            "--language", self.config["language"]
        ]
        try:
            self.logger.info(f"Running Whisper command: {' '.join(command)}")
            subprocess.run(command, check=True)
            self.logger.info("Whisper transcription completed.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error during Whisper transcription: {e}")
            raise


    def analyze_emotions(self, srt_file, work_dir):
        """Perform emotion analysis on the SRT file."""
        self.logger.info(f"Starting emotion analysis for: {srt_file}")

        # Parse subtitles
        subtitles = parse_srt(srt_file)
        self.logger.info(f"Loaded {len(subtitles)} subtitles from SRT file.")

        # Individual sentence emotion analysis
        individual_results = analyze_individual_sentences(
            subtitles=subtitles,
            model_name="uer/roberta-base-finetuned-jd-binary-chinese"
        )

        # Group analysis for individual sentences
        grouped_times_ind, grouped_scores_ind, grouped_texts_ind = group_by_individual_scores(
            individual_results,
            group_size=64,
            step=4
        )

        # Combined group emotion analysis
        grouped_times_comb, grouped_scores_comb, grouped_texts_comb, grouped_labels_comb = group_and_average(
            subtitles=subtitles,
            group_size=64,
            step=4,
            model_name="uer/roberta-base-finetuned-jd-binary-chinese",
            max_length=512
        )

        # Extract highest emotion groups
        positive_highest_ind, negative_highest_ind = extract_highest_groups(
            grouped_times_ind, grouped_scores_ind, grouped_texts_ind
        )
        positive_highest_comb, negative_highest_comb = extract_highest_groups(
            grouped_times_comb, grouped_scores_comb, grouped_texts_comb
        )

        # Save results as JSON
        highest_results = {
            "individual": {
                "positive": positive_highest_ind,
                "negative": negative_highest_ind
            },
            "combined": {
                "positive": positive_highest_comb,
                "negative": negative_highest_comb
            }
        }

        output_json = os.path.join(work_dir, "emotion_highest.json")
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(highest_results, f, ensure_ascii=False, indent=4)
        self.logger.info(f"Emotion analysis results saved to: {output_json}")
        self.logger.info(f"Highest emotion groups: {highest_results}")

        # Plot emotion trends
        plot_file = os.path.join(work_dir, "emotion_trends.png")
        plot_emotion_trends(
            grouped_times_comb,
            grouped_scores_comb,
            grouped_labels_comb,
            positive_highest_comb,
            negative_highest_comb,
            output_file=plot_file
        )
        self.logger.info(f"Emotion trend plot saved to: {plot_file}")

    def process_video_and_analyze(self, input_file):
        """Process video to generate script and perform emotion analysis."""
        file_name = os.path.basename(input_file)
        file_base, _ = os.path.splitext(file_name)
        work_dir = os.path.join(os.path.dirname(input_file), file_base)
        os.makedirs(work_dir, exist_ok=True)

        self.logger.info(f"Working directory created: {work_dir}")

        # Step 1: Convert video to WAV
        wav_file = os.path.join(work_dir, f"{file_base}.wav")
        self.convert_to_wav(input_file, wav_file)

        # Step 2: Transcribe with Whisper
        self.run_whisper(wav_file, work_dir)

        # Step 3: Dynamically find the SRT file
        srt_files = glob.glob(os.path.join(work_dir, "*.srt"))
        if not srt_files:
            self.logger.error(f"No SRT file found in {work_dir}.")
            return

        srt_file = srt_files[0]  # 选择找到的第一个 SRT 文件
        self.logger.info(f"Found SRT file: {srt_file}")

        # Step 4: Analyze emotions on generated SRT
        self.analyze_emotions(srt_file, work_dir)
        if os.path.exists(srt_file):
            self.analyze_emotions(srt_file, work_dir)
        else:
            self.logger.error(f"SRT file not found. Skipping emotion analysis.")
