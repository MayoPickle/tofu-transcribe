import argparse
from config_loader import ConfigLoader
from video.logger_setup import LoggerSetup
from video.video_processor import VideoProcessor
from webserver.webhook_handler import WebhookHandler
from script.parse_srt import parse_srt
from script.emotion_analysis import analyze_individual_sentences, group_and_average, group_by_individual_scores
from script.utils import extract_highest_groups
from script.plot import plot_emotion_trends
class MainApp:
    """Main application entry point."""
    @staticmethod
    def main():
        parser = argparse.ArgumentParser(description="Video to Script Service")
        parser.add_argument("--webserver", action="store_true", help="Start the webserver")
        parser.add_argument("--input", type=str, help="Input video file to process directly")
        parser.add_argument("--config", type=str, default="config.json", help="Path to config file")

        args = parser.parse_args()

        config = ConfigLoader.load_config(args.config)
        logger = LoggerSetup.setup_logger()
        processor = VideoProcessor(config, logger)

        if args.webserver:
            handler = WebhookHandler(processor, config, logger)
            handler.run()
        elif args.input:
            logger.info(f"Processing video file: {args.input}")
            output_dir = processor.process_video(args.input)
            logger.info(f"Transcription completed. Output directory: {output_dir}")
        else:
            logger.error("You must specify either --webserver or --input.")
            parser.print_help()

if __name__ == "__main__":
    MainApp.main()
