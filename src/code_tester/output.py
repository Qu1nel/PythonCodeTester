"""Handles all console output and logging for the application.

This module provides a centralized way to manage user-facing messages and
internal logging. It ensures that all output is consistent and can be
controlled via configuration (e.g., log levels, silent mode).
"""

import logging
import sys
from typing import Literal

from .config import LogLevel

LOG_FORMAT = "%(asctime)s | %(filename)-15s | %(funcName)-15s (%(lineno)-3s) | [%(levelname)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_level: LogLevel) -> logging.Logger:
    """Configures the root logger for the application."""
    logging.basicConfig(level=log_level, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    return logging.getLogger()


class Console:
    """A centralized handler for printing messages to stdout and logging."""

    def __init__(self, logger: logging.Logger, *, is_silent: bool = False):
        """Initializes the Console handler."""
        self._logger = logger
        self._is_silent = is_silent
        self._stdout = sys.stdout

    def print(
        self,
        message: str,
        *,
        level: LogLevel | Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = LogLevel.INFO,
    ) -> None:
        """Prints a message to stdout and logs it simultaneously."""
        level_str = level.value.lower() if isinstance(level, LogLevel) else level.lower()
        log_method = getattr(self._logger, level_str)
        log_method(message)

        if not self._is_silent:
            print(message, file=self._stdout)
