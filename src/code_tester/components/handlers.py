import dataclasses
from typing import Any

from ..config import CheckConfig, Expectation, ExpectConfig
from ..environment import ExecutionEnvironment
from ..output import Console, LogLevel
from ..utils import create_dataclass_from_dict
from .definitions import Action, ActionResult, AssertionFactory, CheckHandler


class ExpectationHandler:
    def __init__(self, config: Expectation, console: Console, assertion_factory: AssertionFactory):
        self._config = config
        self._console = console
        self._assertion_factory = assertion_factory

    def check(self, action_result: ActionResult) -> bool:
        all_passed = True
        expectations_to_check = dataclasses.asdict(self._config)

        for target_name, expect_config_dict in expectations_to_check.items():
            if expect_config_dict is None or not expect_config_dict.get("assertion"):
                continue

            self._console.print(f"  - Verifying target: '{target_name}'...", level=LogLevel.DEBUG)
            actual_value = getattr(action_result, target_name, None)

            expect_config = create_dataclass_from_dict(ExpectConfig, expect_config_dict)

            try:
                assertion = self._assertion_factory.create(expect_config)
                if not assertion.check(actual_value):
                    all_passed = False
                    self._console.print(f"  - ❌ Assertion failed for target '{target_name}'.", level=LogLevel.INFO)
                else:
                    self._console.print(f"  - ✅ Assertion passed for target '{target_name}'.", level=LogLevel.DEBUG)
            except Exception as e:
                self._console.print(
                    f"  - ❌ Error during assertion for '{target_name}': {e}", level=LogLevel.ERROR, exc_info=True
                )
                all_passed = False
        return all_passed


class DefaultCheckHandler(CheckHandler):
    def __init__(self, config: CheckConfig, action: Action, expectation_handler: ExpectationHandler, console: Console):
        self.config = config
        self._action = action
        self._expectation_handler = expectation_handler
        self._console = console
        self._context: dict[str, Any] = {}

    def execute(self, environment: ExecutionEnvironment) -> bool:
        action_result = self._action.execute(environment, self._context)
        return self._expectation_handler.check(action_result)
