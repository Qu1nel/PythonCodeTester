from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from ..config import CheckConfig, ExpectConfig, PerformConfig
from ..environment import ExecutionEnvironment
from .registry import Registry


@dataclass
class ActionResult:
    return_value: Any = None
    stdout: str | None = None
    stderr: str | None = None
    screenshot: Any | None = None  # Placeholder for Pillow.Image object
    http_response: Any | None = None  # Placeholder for Flask response object


@runtime_checkable
class Action(Protocol):
    config: PerformConfig

    def execute(self, environment: ExecutionEnvironment, context: dict[str, Any]) -> ActionResult: ...


@runtime_checkable
class Assertion(Protocol):
    config: ExpectConfig

    def check(self, actual_value: Any) -> bool: ...


@runtime_checkable
class CheckHandler(Protocol):
    config: CheckConfig

    def execute(self, environment: ExecutionEnvironment) -> bool: ...


@runtime_checkable
class AssertionFactory(Protocol):
    @staticmethod
    def create(config: ExpectConfig) -> Assertion: ...


action_registry = Registry[str, Action]()
assertion_registry = Registry[str, Assertion]()
