from typing import Any, Dict, List, Union
from unittest.mock import Mock, MagicMock

from code_tester.config.mocks import MockConfig
from code_tester.utils.exceptions import MockError


class MockFactory:
    
    def create_mock(self, config: MockConfig) -> Mock:
        behavior = config.behavior
        
        valid_keys = {"return_value", "return_object", "side_effect"}
        behavior_keys = set(behavior.keys())
        valid_behavior_keys = behavior_keys & valid_keys
        
        if len(valid_behavior_keys) != 1:
            raise MockError(f"Behavior must contain exactly one of {valid_keys}, got: {list(behavior_keys)}")
        
        behavior_type = list(valid_behavior_keys)[0]
        
        if behavior_type == "return_value":
            return self.create_return_value_mock(behavior["return_value"])
        elif behavior_type == "return_object":
            return self.create_return_object_mock(behavior["return_object"])
        elif behavior_type == "side_effect":
            return self.create_side_effect_mock(behavior["side_effect"])
    
    def create_return_value_mock(self, value: Any) -> Mock:
        mock = Mock()
        mock.return_value = value
        return mock
    
    def create_return_object_mock(self, spec: Dict[str, Any]) -> Mock:
        mock = MagicMock()
        
        if "attributes" in spec:
            for attr_name, attr_value in spec["attributes"].items():
                setattr(mock, attr_name, attr_value)
        
        if "methods" in spec:
            for method_name, method_config in spec["methods"].items():
                method_mock = Mock()
                if "return_value" in method_config:
                    method_mock.return_value = method_config["return_value"]
                elif "side_effect" in method_config:
                    method_mock.side_effect = self._create_side_effect(method_config["side_effect"])
                setattr(mock, method_name, method_mock)
        
        return mock
    
    def create_side_effect_mock(self, side_effect_config: Dict[str, Any]) -> Mock:
        mock = Mock()
        mock.side_effect = self._create_side_effect(side_effect_config)
        return mock
    
    def _create_side_effect(self, config: Dict[str, Any]) -> Union[Exception, List[Any]]:
        if "raises_exception" in config:
            exception_config = config["raises_exception"]
            exception_type = exception_config.get("type", "Exception")
            exception_message = exception_config.get("message", "Mock exception")
            
            if exception_type == "ConnectionError":
                return ConnectionError(exception_message)
            elif exception_type == "ValueError":
                return ValueError(exception_message)
            elif exception_type == "RuntimeError":
                return RuntimeError(exception_message)
            else:
                return Exception(exception_message)
        
        elif "sequence" in config:
            sequence = []
            for item in config["sequence"]:
                if "return_value" in item:
                    sequence.append(item["return_value"])
                elif "raises_exception" in item:
                    sequence.append(self._create_side_effect(item))
            return sequence
        
        else:
            raise MockError(f"Unsupported side_effect configuration: {config}")