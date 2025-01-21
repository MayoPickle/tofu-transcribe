import os
import subprocess

class VideoProcessor:
    """Class to handle video processing tasks."""
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

    def process_video(self, input_file):
        file_name = os.path.basename(input_file)
        file_base, _ = os.path.splitext(file_name)
        work_dir = os.path.join(os.path.dirname(input_file), file_base)
        os.makedirs(work_dir, exist_ok=True)
        self.logger.info(f"Working directory created: {work_dir}")

        wav_file = os.path.join(work_dir, f"{file_base}.wav")
        self.convert_to_wav(input_file, wav_file)

        self.run_whisper(wav_file, work_dir)

        self.logger.info(f"Processing completed. Output files saved in: {work_dir}")
        return work_dir
