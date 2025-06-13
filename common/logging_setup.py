import os
import logging

def setup_logging(log_dir="logs", log_file="trace_parser.log"):
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

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
