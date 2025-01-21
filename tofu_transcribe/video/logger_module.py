import logging

def setup_logger(log_file="application.log", log_level=logging.INFO):
    """
    Set up a logger with file handler and stream handler.
    """
    # Create a custom logger
    logger = logging.getLogger("custom_logger")
    logger.setLevel(log_level)

    # Prevent creating duplicate handlers
    if not logger.handlers:
        # Create a file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Create a console handler (optional, for debugging)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
