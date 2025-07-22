from functools import wraps
from typing import Callable, TypeVar, ParamSpec

from .logger import get_logger
from .config import LogLevel

P = ParamSpec("P")
T = TypeVar("T")


def log_initialization(
    level: LogLevel = LogLevel.DEBUG,
    start_message: str = "Initializing {class_name}...",
    end_message: str = "{class_name} initialized."
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(init_method: Callable[P, T]) -> Callable[P, T]:
        @wraps(init_method)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__
            else:
                class_name = "Unknown"
            
            logger = get_logger()
            
            log_method = getattr(logger, level.lower())
            log_method(start_message.format(class_name=class_name))
            
            result = init_method(*args, **kwargs)
            
            log_method(end_message.format(class_name=class_name))
            
            return result
        
        return wrapper
    
    return decorator