from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any


class ExitCode(IntEnum):
    SUCCESS = 0
    TESTS_FAILED = 1
    FILE_NOT_FOUND = 2
    JSON_ERROR = 3
    UNEXPECTED_ERROR = 10


class LogLevel(StrEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AppConfig:
    solution_path: Path
    test_case_path: Path
    log_level: LogLevel
    is_quiet: bool
    exit_on_first_error: bool
    max_messages: int = 0


@dataclass(frozen=True)
class PerformConfig:
    action: str
    target: str | dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    save_as: str | None = None
    start_from_object_ref: str | None = None


@dataclass(frozen=True)
class ExpectConfig:
    assertion: str
    value: Any | None = None
    target_mock: str | None = None
    tolerance: float | None = None


@dataclass(frozen=True)
class Expectation:
    return_value: ExpectConfig | None = None
    stdout: ExpectConfig | None = None
    stderr: ExpectConfig | None = None
    image: ExpectConfig | None = None
    http_response: ExpectConfig | None = None
    mock_calls: list[ExpectConfig] | None = None


@dataclass(frozen=True)
class MockConfig:
    target_path: str
    behavior: dict[str, Any]
    save_as: str | None = None


@dataclass(frozen=True)
class CheckSpec:
    perform: PerformConfig
    expect: Expectation
    mocks: list[MockConfig] = field(default_factory=list)


@dataclass(frozen=True)
class CheckConfig:
    check_id: int
    name_for_output: str
    reason_for_output: str
    explain_for_error: str
    spec: CheckSpec
    is_critical: bool = False


@dataclass(frozen=True)
class TestCaseConfig:
    test_id: int
    test_name: str
    description: str
    test_type: str
    checks: list[CheckConfig]
    setup_actions: list[dict[str, Any]] = field(default_factory=list)
