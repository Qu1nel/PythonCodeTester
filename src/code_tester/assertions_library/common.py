from typing import Any

from ..components.definitions import Assertion, assertion_registry
from ..config import ExpectConfig


@assertion_registry.register("equals")
class EqualsAssertion(Assertion):
    def __init__(self, config: ExpectConfig):
        self.config = config

    def check(self, actual_value: Any) -> bool:
        expected_value = self.config.value

        if isinstance(actual_value, str) and isinstance(expected_value, str):
            return actual_value.strip() == expected_value.strip()

        return actual_value == expected_value
