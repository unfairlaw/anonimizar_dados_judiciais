"""Logging utilities for the RAG ecosystem."""

import logging
import sys
from typing import Optional
from pathlib import Path
from rag_ecosystem.config.settings import get_settings


def setup_logger(name: str = "rag_ecosystem",
                log_file: Optional[str] = None,
                log_level: Optional[str] = None) -> logging.Logger:
    """Setup a logger with appropriate handlers.

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger
    """
    settings = get_settings()

    if log_level is None:
        log_level = settings.log_level

    if log_file is None:
        log_file = settings.log_file

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
