import sys
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger as loguru_logger

from .config import LogConfig, LogLevel
from .formatters import ConsoleFormatter, FileFormatter, JsonFormatter

# Context variables for structured logging
trace_id_var: ContextVar[str] = ContextVar('trace_id', default='')
test_case_var: ContextVar[str] = ContextVar('test_case', default='')
check_id_var: ContextVar[str] = ContextVar('check_id', default='')


class Logger:
    def __init__(self, name: str, config: LogConfig):
        self.name = name
        self.config = config
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        # Remove default handler
        loguru_logger.remove()
        
        # Add console handler if enabled
        if self.config.console_enabled:
            console_format = self._get_console_format()
            loguru_logger.add(
                sys.stderr,
                format=console_format,
                level=self.config.level,
                colorize=self.config.colorize,
                filter=self._add_context
            )
        
        # Add file handler if enabled
        if self.config.file_enabled and self.config.file_path:
            file_format = self._get_file_format()
            loguru_logger.add(
                self.config.file_path,
                format=file_format,
                level=self.config.level,
                rotation=self.config.file_rotation,
                retention=self.config.file_retention,
                filter=self._add_context
            )
    
    def _get_console_format(self) -> str:
        if self.config.colorize:
            return (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[trace_id]}</cyan> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        else:
            return (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{extra[trace_id]} | "
                "{name}:{function}:{line} | "
                "{message}"
            )
    
    def _get_file_format(self) -> str:
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{process} | "
            "{thread} | "
            "{extra[trace_id]} | "
            "{extra[test_case]} | "
            "{extra[check_id]} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
    
    def _add_context(self, record: Dict[str, Any]) -> bool:
        record["extra"]["trace_id"] = trace_id_var.get() or "main"
        record["extra"]["test_case"] = test_case_var.get() or ""
        record["extra"]["check_id"] = check_id_var.get() or ""
        return True
    
    def trace(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).trace(message)
    
    def debug(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).debug(message)
    
    def info(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).info(message)
    
    def success(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).success(message)
    
    def warning(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).warning(message)
    
    def error(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).error(message)
    
    def critical(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).critical(message)
    
    def exception(self, message: str, **kwargs) -> None:
        loguru_logger.bind(**kwargs).exception(message)


# Global logger instance
_logger: Optional[Logger] = None


def setup_logger(config: LogConfig) -> Logger:
    global _logger
    _logger = Logger("code_tester", config)
    return _logger


def get_logger() -> Logger:
    if _logger is None:
        raise RuntimeError("Logger not initialized. Call setup_logger() first.")
    return _logger


def set_trace_id(trace_id: str) -> None:
    trace_id_var.set(trace_id)


def set_test_case(test_case: str) -> None:
    test_case_var.set(test_case)


def set_check_id(check_id: str) -> None:
    check_id_var.set(check_id)


def generate_trace_id() -> str:
    return str(uuid.uuid4())[:8]