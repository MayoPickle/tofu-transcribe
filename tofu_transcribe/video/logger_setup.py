import logging

class LoggerSetup:
    """Class to handle logging setup."""
    @staticmethod
    def setup_logger():
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("video2script_service")
