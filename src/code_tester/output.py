import argparse
import logging
import sys
from functools import wraps
from typing import Callable, Concatenate, Literal, ParamSpec, TypeVar

from .config import LogLevel

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = (
    "{asctime}.{msecs:03.0f} | "
    "{levelname:^8} | "
    "[{processName}({process})/{threadName}({thread})] | "
    "{filename}:{funcName}:{lineno} | "
    "{message}"
)

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)


logging.Logger.trace = trace


def log_level_type(value: str) -> LogLevel:
    match value.upper():
        case LogLevel.TRACE:
            return LogLevel.TRACE
        case LogLevel.DEBUG:
            return LogLevel.DEBUG
        case LogLevel.INFO:
            return LogLevel.INFO
        case LogLevel.WARNING:
            return LogLevel.WARNING
        case LogLevel.ERROR:
            return LogLevel.ERROR
        case LogLevel.CRITICAL:
            return LogLevel.CRITICAL
        case _:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid log level.")


def setup_logging(log_level: LogLevel) -> logging.Logger:
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT, style="{")

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

    return root_logger


P = ParamSpec("P")
T_self = TypeVar("T_self")


def log_initialization(
    level: LogLevel | Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = LogLevel.TRACE,
    start_message: str = "Initializing {class_name}...",
    end_message: str = "{class_name} initialized.",
) -> Callable[[Callable[Concatenate[T_self, P], None]], Callable[Concatenate[T_self, P], None]]:
    def decorator(init_method: Callable[Concatenate[T_self, P], None]) -> Callable[Concatenate[T_self, P], None]:
        @wraps(init_method)
        def wrapper(self: T_self, *args: P.args, **kwargs: P.kwargs) -> None:
            class_name = self.__class__.__name__
            logger = logging.getLogger(self.__class__.__module__)
            level_num = logging.getLevelName(level if isinstance(level, LogLevel) else level)

            logger.log(level_num, start_message.format(class_name=class_name))
            result = init_method(self, *args, **kwargs)
            logger.log(level_num, end_message.format(class_name=class_name))

            return result

        return wrapper

    return decorator


class Console:
    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, logger: logging.Logger, *, is_quiet: bool = False, show_verdict: bool = True):
        self._logger = logger
        self._is_quiet = is_quiet
        self._show_verdict = show_verdict
        self._stdout = sys.stdout

    def should_print(self, is_verdict: bool, show_user: bool) -> bool:
        return (not self._is_quiet) and ((not is_verdict and show_user) or (is_verdict and self._show_verdict))

    def print(
        self,
        message: str,
        *,
        level: LogLevel | Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = LogLevel.TRACE,
        is_verdict: bool = False,
        show_user: bool = False,
        exc_info: bool = False,
    ) -> None:
        level_num = logging.getLevelName(level if isinstance(level, LogLevel) else level)
        self._logger.log(level_num, message, stacklevel=2, exc_info=exc_info)

        if self.should_print(is_verdict, show_user):
            print(message, file=self._stdout)
