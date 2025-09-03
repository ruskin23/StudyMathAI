import logging
import os
from pathlib import Path


def get_logger(name: str = "studymathai") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True, parents=True)
        file_handler = logging.FileHandler(log_dir / "studymathai.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger
