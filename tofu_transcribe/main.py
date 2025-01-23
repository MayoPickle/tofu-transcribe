import os
import argparse
from config_loader import ConfigLoader
from video.logger_setup import LoggerSetup
from video.video_processor import VideoProcessor
from video.emotion_analyzer import EmotionAnalyzer
from webserver.webhook_handler import WebhookHandler


class MainApp:
    """Main application entry point."""

    @staticmethod
    def main():
        # Set environment variable for threading
        os.environ["MKL_THREADING_LAYER"] = "GNU"

        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Video to Script Service")
        parser.add_argument("--webserver", action="store_true", help="Start the webserver")
        parser.add_argument("--input", type=str, help="Input video file to process directly")
        parser.add_argument("--config", type=str, default="config.json", help="Path to config file")

        args = parser.parse_args()

        # Load configuration and logger
        config = ConfigLoader.load_config(args.config)
        logger = LoggerSetup.setup_logger()

        # Initialize VideoProcessor and EmotionAnalyzer
        video_processor = VideoProcessor(config, logger)
        emotion_analyzer = EmotionAnalyzer(config, logger)

        if args.webserver:
            # Run the webserver if specified
            handler = WebhookHandler(video_processor, emotion_analyzer, config, logger)
            handler.run()
        elif args.input:
            # Process input video file
            logger.info(f"Processing video file: {args.input}")

            # Step 1: Prepare work directory
            work_dir = video_processor.prepare_work_dir(args.input)

            # Step 2: Convert video to WAV
            wav_file = os.path.join(work_dir, "tofu_transcribe.wav")
            video_processor.convert_to_wav(args.input, wav_file)

            # Step 3: Transcribe with Whisper
            video_processor.run_whisper(wav_file, work_dir)

            # Step 4: Find SRT file and analyze emotions
            srt_file = video_processor.find_srt_file(work_dir)
            if srt_file:
                emotion_analyzer.process_speech_emotions(work_dir)
                emotion_analyzer.analyze_emotions(srt_file, work_dir)
                logger.info(f"Processing completed. Results saved in: {work_dir}")

            else:
                logger.error(f"No SRT file found in {work_dir}. Emotion analysis skipped.")
        else:
            # Show help if no arguments provided
            logger.error("You must specify either --webserver or --input.")
            parser.print_help()


if __name__ == "__main__":
    MainApp.main()
