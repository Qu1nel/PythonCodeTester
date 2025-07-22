from enum import StrEnum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class LogLevel(StrEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG" 
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogConfig(BaseModel):
    level: LogLevel = LogLevel.INFO
    console_enabled: bool = True
    file_enabled: bool = False
    file_path: Optional[Path] = None
    file_rotation: str = "10 MB"
    file_retention: str = "1 week"
    show_trace: bool = False
    colorize: bool = True
    format_template: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    class Config:
        use_enum_values = True