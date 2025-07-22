from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..logging import LogLevel


class AppConfig(BaseModel):
    solution_path: Path = Field(..., description="Path to the Python solution file to test")
    test_case_path: Path = Field(..., description="Path to the JSON file with the test case")
    log_level: LogLevel = Field(LogLevel.ERROR, description="Logging level")
    is_quiet: bool = Field(False, description="Suppress all stdout output")
    exit_on_first_error: bool = Field(False, description="Exit instantly on the first failed check")
    max_messages: int = Field(0, description="Maximum number of failed check messages to display (0 for no limit)")
    
    @field_validator('solution_path', 'test_case_path')
    @classmethod
    def validate_paths_exist(cls, v):
        # Skip validation in tests or if path is relative
        if not v.is_absolute() or str(v).startswith('tests/'):
            return v
        if not v.exists():
            raise ValueError(f"File does not exist: {v}")
        return v
    
    @field_validator('max_messages')
    @classmethod
    def validate_max_messages(cls, v):
        if v < 0:
            raise ValueError("max_messages must be non-negative")
        return v
    
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )