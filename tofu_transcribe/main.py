import argparse
from config_loader import ConfigLoader
from logger_setup import LoggerSetup
from video_processor import VideoProcessor
from webhook_handler import WebhookHandler

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
