"""Defines the core component interfaces for the tester using Protocols.

This module establishes the "contracts" for the main architectural components
of the dynamic tester: Actions and Assertions. It also defines the standard
data structure, `ActionResult`, used to pass results between them.
"""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from ..config import ExpectConfig, PerformConfig


@dataclass
class ActionResult:
    """A standard container for all possible outcomes of a performed Action.

    This dataclass acts as a universal transport object, allowing any Action
    to return multiple types of results (e.g., a function's return value and
    its stdout output) simultaneously. Assertions can then inspect the specific
    field they are designed to check.

    Attributes:
        return_value: The value returned by a function call.
        stdout: Any text captured from the standard output stream.
        stderr: Any text captured from the standard error stream.
        screenshot: A Pillow Image object, captured in an Arcade test.
        http_response: A response object from a Flask test client.
    """
    return_value: Any = None
    stdout: str | None = None
    stderr: str | None = None
    screenshot: Any | None = None  # Pillow.Image
    http_response: Any | None = None  # Flask response object


@runtime_checkable
class Action(Protocol):
    """An interface for objects that perform a single, dynamic action.

    An Action's responsibility is to execute a piece of the student's code in
    a controlled environment and capture all relevant outcomes (return value,
    I/O, etc.) into an `ActionResult` object.
    """

    config: PerformConfig

    def execute(self) -> ActionResult:
        """Executes the defined action.

        This method should handle setting up the environment (e.g., providing
        stdin), running the code, capturing all outputs, and returning them
        in a structured `ActionResult` object.

        Returns:
            An `ActionResult` instance containing the outcomes of the action.
        """
        ...


@runtime_checkable
class Assertion(Protocol):
    """An interface for objects that verify an outcome against an expectation.

    An Assertion takes the `ActionResult` produced by an Action and a specific
    expectation from the JSON test case (e.g., the part for `return_value` or
    `stdout`). It then performs a comparison and returns a boolean result.
    """

    config: ExpectConfig

    def check(self, result: ActionResult) -> bool:
        """Checks if a specific part of the action's result meets the expectation.

        Args:
            result: The `ActionResult` object produced by the Action.

        Returns:
            True if the assertion passes, False otherwise.
        """
        ...