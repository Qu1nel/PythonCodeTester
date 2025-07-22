from typing import Any

from ..core import ComponentMetadata, ComponentProvider, DependencyContainer, plugin_provider
from ..config import ExpectConfig


class Assertion:
    def __init__(self, config: ExpectConfig):
        self.config = config
    
    def check(self, actual_value: Any) -> bool:
        raise NotImplementedError


class EqualsAssertion(Assertion):
    def check(self, actual_value: Any) -> bool:
        expected_value = self.config.value

        if isinstance(actual_value, str) and isinstance(expected_value, str):
            return actual_value.strip() == expected_value.strip()

        return actual_value == expected_value


class ContainsAssertion(Assertion):
    def check(self, actual_value: Any) -> bool:
        expected_value = self.config.value
        
        if isinstance(actual_value, str):
            return expected_value in actual_value
        elif isinstance(actual_value, (list, tuple)):
            return expected_value in actual_value
        elif isinstance(actual_value, dict):
            return expected_value in actual_value
        
        return False


class IsInRangeAssertion(Assertion):
    def check(self, actual_value: Any) -> bool:
        if not isinstance(actual_value, (int, float)):
            return False
        
        range_config = self.config.value
        if not isinstance(range_config, dict) or "min" not in range_config or "max" not in range_config:
            return False
        
        min_val = range_config["min"]
        max_val = range_config["max"]
        
        return min_val <= actual_value <= max_val


class IsCloseToAssertion(Assertion):
    def check(self, actual_value: Any) -> bool:
        if not isinstance(actual_value, (int, float)):
            return False
        
        expected_value = self.config.value
        tolerance = self.config.tolerance or 1e-9
        
        return abs(actual_value - expected_value) <= tolerance


class IsInstanceOfAssertion(Assertion):
    def check(self, actual_value: Any) -> bool:
        expected_type_name = self.config.value
        
        if isinstance(expected_type_name, str):
            return type(actual_value).__name__ == expected_type_name
        
        return isinstance(actual_value, expected_type_name)


class RaisesExceptionAssertion(Assertion):
    def check(self, actual_value: Any) -> bool:
        if not isinstance(actual_value, Exception):
            return False
        
        expected_exception_name = self.config.value
        
        if isinstance(expected_exception_name, str):
            return type(actual_value).__name__ == expected_exception_name
        
        return isinstance(actual_value, expected_exception_name)


@plugin_provider(ComponentMetadata(
    name="core_assertions",
    version="1.0.0",
    test_types=["py_general", "api", "flask", "arcade"]
))
class CoreAssertionsProvider(ComponentProvider):
    def register_components(self, container: DependencyContainer) -> None:
        assertion_factories = {
            "equals": EqualsAssertion,
            "contains": ContainsAssertion,
            "is_in_range": IsInRangeAssertion,
            "is_close_to": IsCloseToAssertion,
            "is_instance_of": IsInstanceOfAssertion,
            "raises_exception": RaisesExceptionAssertion,
        }
        
        for assertion_name, assertion_class in assertion_factories.items():
            container.register_factory(
                f"assertion_{assertion_name}",
                lambda cls=assertion_class: cls
            )