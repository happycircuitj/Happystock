"""Logging utilities for the divergence scanner."""
from __future__ import annotations

import logging
from typing import Optional


DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def get_logger(name: str, level: int = logging.INFO, fmt: str = DEFAULT_LOG_FORMAT) -> logging.Logger:
    """Create or retrieve a configured logger.

    Args:
        name: Logger name.
        level: Logging level.
        fmt: Logging format string.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def configure_root_logger(level: int = logging.INFO, fmt: Optional[str] = None) -> None:
    """Configure the root logger for the application.

    Args:
        level: Logging level.
        fmt: Optional format string.
    """
    logging.basicConfig(level=level, format=fmt or DEFAULT_LOG_FORMAT)
