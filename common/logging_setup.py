"""
logging_setup.py

Configures and returns a logger that outputs messages to both a file and the console.

Functions:
    - setup_logging(log_dir="logs", log_file="trace_parser.log"):
        Creates a logger with file and console handlers using standard formatting.
"""

import os
import logging

def setup_logging(log_dir: str = "logs", log_file: str = "trace_parser.log") -> logging.Logger:   
    """
    Sets up and returns a logger that writes to both a log file and the console.

    This function ensures logs are stored persistently in a specified directory and also printed to the screen.
    If the logger has already been configured, it avoids adding duplicate handlers.

    Args:
        log_dir (str): Directory to store the log file. Defaults to 'logs'.
        log_file (str): Name of the log file. Defaults to 'trace_parser.log'.

    Returns:
        logging.Logger: Configured logger instance.
    """
    import logging
    import os
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Only add handlers once
    if not logger.handlers:
        log_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        file_handler = logging.FileHandler(os.path.join(log_dir, log_file), mode="w", encoding="utf-8")
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
