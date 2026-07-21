"""
logger.py
---------
Centralized logging setup. Every module calls get_logger(__name__)
to get a consistently formatted logger that writes to both console
and a rotating log file under /logs.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from config import LOG_DIR

_LOG_FILE = LOG_DIR / "claimwise.log"

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger with console + file handlers attached once."""
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured (avoid duplicate handlers on re-import / Streamlit reruns)
        return logger

    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(_FORMATTER)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        _LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(_FORMATTER)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
