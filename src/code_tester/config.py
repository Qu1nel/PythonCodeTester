from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any


class ExitCode(IntEnum):
    """Defines standardized exit codes for the command-line application."""
    SUCCESS = 0
    TESTS_FAILED = 1
    FILE_NOT_FOUND = 2
    JSON_ERROR = 3
    UNEXPECTED_ERROR = 10


class LogLevel(StrEnum):
    """Defines the supported logging levels for the application."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AppConfig:
    """Stores the main application configuration from CLI arguments."""
    solution_path: Path
    test_case_path: Path
    log_level: LogLevel
    is_silent: bool
    stop_on_first_fail: bool


@dataclass(frozen=True)
class PerformConfig:
    """Represents the 'perform' block, defining the action to execute."""
    action: str
    target: str | dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    save_as: str | None = None
    # Новое поле для зависимостей в Arcade
    start_from_object_ref: str | None = None


@dataclass(frozen=True)
class ExpectConfig:
    """Represents an 'expect' block, defining an assertion."""
    assertion: str
    value: Any | None = None
    target_mock: str | None = None
    tolerance: float | None = None


@dataclass(frozen=True)
class Expectation:
    """Represents the full expectation, which can check return value and stdout."""
    return_value: ExpectConfig | None = None
    stdout: ExpectConfig | None = None
    stderr: ExpectConfig | None = None
    image: ExpectConfig | None = None
    http_response: ExpectConfig | None = None
    mock_calls: list[ExpectConfig] | None = None


@dataclass(frozen=True)
class MockConfig:
    """Represents a 'mock' object configuration."""
    target_path: str
    behavior: dict[str, Any]
    save_as: str | None = None


@dataclass(frozen=True)
class CheckSpec:
    """Represents the 'spec' block within a check."""
    perform: PerformConfig
    expect: Expectation
    mocks: list[MockConfig] | None = None


@dataclass(frozen=True)
class CheckConfig:
    """Represents a single 'check' within a test case."""
    check_id: int
    name_for_output: str
    reason_for_output: str
    explain_for_error: str
    spec: CheckSpec
    is_critical: bool = False


@dataclass(frozen=True)
class TestCaseConfig:
    """Represents a full test case loaded from a JSON file."""
    test_id: int
    test_name: str
    description: str
    test_type: str
    checks: list[CheckConfig]
    setup_actions: list[dict[str, Any]] = field(default_factory=list)