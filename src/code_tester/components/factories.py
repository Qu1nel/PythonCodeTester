"""Contains factories for creating Action and Assertion objects.

This module implements the Factory Method design pattern to decouple the core
tester engine from the concrete implementations of its components.
"""

from ..config import ExpectConfig, PerformConfig
# from ..exceptions import TestCaseError
from .definitions import Action, Assertion


class ActionFactory:
    """Creates Action objects from a 'perform' configuration block."""

    def __init__(self, config: PerformConfig):
        """Initializes the factory with the action's configuration."""
        self._config = config

    def create(self) -> Action:
        """Creates a specific Action instance based on its type."""
        # TODO: Реализовать match-case для 'run_script', 'call_function', etc.
        # from ..actions_library.io_actions import RunScriptAction
        # match self._config.action:
        #     case "run_script":
        #         return RunScriptAction(self._config)
        #     ...
        raise NotImplementedError(f"Action '{self._config.action}' not implemented.")


class AssertionFactory:
    """Creates a specific Assertion object for a single expectation."""

    def __init__(self, config: ExpectConfig):
        """Initializes the factory with the assertion's configuration."""
        self._config = config

    def create(self) -> Assertion:
        """Creates a specific Assertion instance based on its type."""
        # TODO: Реализовать match-case для 'equals', 'contains', 'is_close_to', etc.
        # from ..assertions_library.common import EqualsAssertion
        # match self._config.assertion:
        #     case "equals":
        #         return EqualsAssertion(self._config)
        #     ...
        raise NotImplementedError(f"Assertion '{self._config.assertion}' not implemented.")