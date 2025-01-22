import os
import glob
import subprocess


class VideoProcessor:
    """Handles video processing tasks like audio extraction and transcription."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def _run_command(self, command, error_message):
        """Run a shell command and handle errors."""
        try:
            self.logger.info(f"Running command: {' '.join(command)}")
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"{error_message}: {e}")
            raise

    def convert_to_wav(self, input_file, output_wav):
        """Convert a video file to WAV format."""
        if os.path.exists(output_wav):
            self.logger.warning(f"Output WAV file already exists. Overwriting: {output_wav}")
            os.remove(output_wav)

        command = [
            "ffmpeg", "-i", input_file,
            "-ar", str(self.config["ffmpeg_options"]["sample_rate"]),
            "-ac", str(self.config["ffmpeg_options"]["channels"]),
            output_wav
        ]
        self._run_command(command, "Error during WAV conversion")
        self.logger.info(f"Converted video to WAV: {output_wav}")

    def run_whisper(self, file_path, output_dir):
        """Run Whisper for transcription."""
        os.makedirs(output_dir, exist_ok=True)
        self._cleanup_existing_files(output_dir, ["srt", "json", "txt"])

        command = [
            "whisper", file_path,
            "--model", self.config["model"],
            "--device", self.config["device"],
            "--output_dir", output_dir,
            "--language", self.config["language"]
        ]
        self._run_command(command, "Error during Whisper transcription")
        self.logger.info("Whisper transcription completed.")

    def _cleanup_existing_files(self, directory, extensions):
        """Remove existing files with specific extensions in a directory."""
        for ext in extensions:
            for file in glob.glob(os.path.join(directory, f"*.{ext}")):
                self.logger.warning(f"Output file already exists. Overwriting: {file}")
                os.remove(file)

    def prepare_work_dir(self, input_file):
        """Prepare working directory for the input video file."""
        file_name = os.path.basename(input_file)
        work_dir = os.path.join(os.path.dirname(input_file), os.path.splitext(file_name)[0])
        os.makedirs(work_dir, exist_ok=True)
        self.logger.info(f"Working directory created: {work_dir}")
        return work_dir

    def find_srt_file(self, work_dir):
        """Find the first SRT file in the working directory."""
        srt_files = glob.glob(os.path.join(work_dir, "*.srt"))
        if not srt_files:
            self.logger.error(f"No SRT file found in {work_dir}.")
            return None
        self.logger.info(f"Found SRT file: {srt_files[0]}")
        return srt_files[0]
