import unittest
from decimal import Decimal

from src.code_tester.config import ExpectConfig
from src.code_tester.plugins.core_assertions import (
    ContainsAssertion,
    EqualsAssertion,
    IsCloseToAssertion,
    IsInRangeAssertion,
    IsInstanceOfAssertion,
    RaisesExceptionAssertion,
)


class TestAllAssertionsComprehensive(unittest.TestCase):

    def test_equals_assertion_comprehensive(self):
        test_cases = [
            # Numbers
            {"value": 42, "test_cases": [
                (42, True),
                (42.0, True),
                (43, False),
                ("42", False)
            ]},
            # Strings
            {"value": "hello", "test_cases": [
                ("hello", True),
                ("  hello  ", True),  # Should strip whitespace
                ("Hello", False),
                ("hello world", False),
                (42, False)
            ]},
            # Lists
            {"value": [1, 2, 3], "test_cases": [
                ([1, 2, 3], True),
                ([1, 2, 3, 4], False),
                ([3, 2, 1], False),  # Order matters
                ((1, 2, 3), False),  # Different type
                ("123", False)
            ]},
            # Dictionaries
            {"value": {"a": 1, "b": 2}, "test_cases": [
                ({"a": 1, "b": 2}, True),
                ({"b": 2, "a": 1}, True),  # Order doesn't matter for dicts
                ({"a": 1}, False),
                ({"a": 1, "b": 2, "c": 3}, False)
            ]},
            # Booleans
            {"value": True, "test_cases": [
                (True, True),
                (False, False),
                (1, True),  # In Python, True == 1
                ("True", False)
            ]},
            # None
            {"value": None, "test_cases": [
                (None, True),
                (0, False),
                ("", False),
                (False, False)
            ]}
        ]
        
        for case in test_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(expected=case["value"], actual=test_value):
                    config = ExpectConfig(assertion="equals", value=case["value"])
                    assertion = EqualsAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)

    def test_contains_assertion_comprehensive(self):
        test_cases = [
            # String contains
            {"container_type": "string", "value": "world", "test_cases": [
                ("hello world", True),
                ("world peace", True),
                ("WORLD", False),  # Case sensitive
                ("word", False),
                ("", False),
                (123, False)  # Wrong type
            ]},
            # List contains
            {"container_type": "list", "value": 42, "test_cases": [
                ([1, 42, 3], True),
                ([42], True),
                ([1, 2, 3], False),
                ([], False),
                ("42", True),  # String contains str(42) = "42"
                (42, False)  # Not a container
            ]},
            # Tuple contains
            {"container_type": "tuple", "value": "test", "test_cases": [
                (("hello", "test", "world"), True),
                (("test",), True),
                (("TEST",), False),  # Case sensitive
                ((), False),
                (["test"], True)  # List also supports 'in' operator
            ]},
            # Dict contains (keys)
            {"container_type": "dict", "value": "key1", "test_cases": [
                ({"key1": "value1", "key2": "value2"}, True),
                ({"key1": None}, True),
                ({"KEY1": "value1"}, False),  # Case sensitive
                ({}, False),
                ({"value1": "key1"}, False),  # Checks keys, not values
                ([("key1", "value1")], False)  # Wrong type
            ]},
            # Complex objects
            {"container_type": "mixed", "value": [1, 2], "test_cases": [
                ([[1, 2], [3, 4]], True),
                ([[3, 4], [1, 2]], True),
                ([[1, 2, 3]], False),
                ([1, 2], False),  # Not a container of the value
                ("12", False)
            ]}
        ]
        
        for case in test_cases:
            for test_container, expected_result in case["test_cases"]:
                with self.subTest(container_type=case["container_type"], 
                                value=case["value"], container=test_container):
                    config = ExpectConfig(assertion="contains", value=case["value"])
                    assertion = ContainsAssertion(config)
                    
                    result = assertion.check(test_container)
                    self.assertEqual(result, expected_result)

    def test_is_in_range_assertion_comprehensive(self):
        test_cases = [
            # Integer ranges
            {"range": {"min": 1, "max": 10}, "test_cases": [
                (5, True),
                (1, True),  # Boundary
                (10, True),  # Boundary
                (0, False),
                (11, False),
                (-5, False)
            ]},
            # Float ranges
            {"range": {"min": 0.0, "max": 1.0}, "test_cases": [
                (0.5, True),
                (0.0, True),  # Boundary
                (1.0, True),  # Boundary
                (0.999, True),
                (1.001, False),
                (-0.1, False)
            ]},
            # Mixed int/float ranges
            {"range": {"min": -10, "max": 10.5}, "test_cases": [
                (0, True),
                (-10, True),
                (10.5, True),
                (10.6, False),
                (-10.1, False)
            ]},
            # Large numbers
            {"range": {"min": 1000000, "max": 2000000}, "test_cases": [
                (1500000, True),
                (1000000, True),
                (2000000, True),
                (999999, False),
                (2000001, False)
            ]}
        ]
        
        for case in test_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(range=case["range"], value=test_value):
                    config = ExpectConfig(assertion="is_in_range", value=case["range"])
                    assertion = IsInRangeAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)

    def test_is_in_range_assertion_invalid_inputs(self):
        invalid_cases = [
            # Non-numeric values
            {"range": {"min": 1, "max": 10}, "test_cases": [
                ("5", False),
                ("hello", False),
                ([5], False),
                (None, False),
                (True, False)
            ]},
            # Invalid range configurations
            {"range": {"min": 1}, "test_cases": [(5, False)]},  # Missing max
            {"range": {"max": 10}, "test_cases": [(5, False)]},  # Missing min
            {"range": "invalid", "test_cases": [(5, False)]},  # Wrong type
        ]
        
        for case in invalid_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(range=case["range"], value=test_value):
                    config = ExpectConfig(assertion="is_in_range", value=case["range"])
                    assertion = IsInRangeAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)

    def test_is_close_to_assertion_comprehensive(self):
        test_cases = [
            # Default tolerance (1e-9)
            {"target": 3.14159, "tolerance": None, "test_cases": [
                (3.14159, True),
                (3.141590000000001, True),  # Within default tolerance
                (3.14160, False),
                (3.14158, False)
            ]},
            # Custom tolerance
            {"target": 100.0, "tolerance": 0.1, "test_cases": [
                (100.0, True),
                (100.05, True),
                (99.95, True),
                (100.1, True),  # Boundary
                (99.9, True),   # Boundary
                (100.11, False),
                (99.89, False)
            ]},
            # Integer targets
            {"target": 50, "tolerance": 2, "test_cases": [
                (50, True),
                (52, True),
                (48, True),
                (53, False),
                (47, False)
            ]},
            # Very small numbers
            {"target": 0.001, "tolerance": 0.0001, "test_cases": [
                (0.001, True),
                (0.0011, False),
                (0.0009, False),
                (0.00105, True)
            ]},
            # Negative numbers
            {"target": -10.5, "tolerance": 0.5, "test_cases": [
                (-10.5, True),
                (-10.0, True),
                (-11.0, True),
                (-9.9, False),
                (-11.1, False)
            ]}
        ]
        
        for case in test_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(target=case["target"], tolerance=case["tolerance"], value=test_value):
                    config = ExpectConfig(
                        assertion="is_close_to", 
                        value=case["target"],
                        tolerance=case["tolerance"]
                    )
                    assertion = IsCloseToAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)

    def test_is_close_to_assertion_invalid_inputs(self):
        invalid_cases = [
            {"target": 10.0, "tolerance": 0.1, "test_cases": [
                ("10.0", False),
                ("hello", False),
                ([10.0], False),
                (None, False),
                (True, False)
            ]}
        ]
        
        for case in invalid_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(target=case["target"], value=test_value):
                    config = ExpectConfig(assertion="is_close_to", value=case["target"], tolerance=case["tolerance"])
                    assertion = IsCloseToAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)

    def test_is_instance_of_assertion_comprehensive(self):
        class CustomClass:
            pass
        
        class ChildClass(CustomClass):
            pass
        
        test_cases = [
            # Built-in types by string name
            {"type_name": "int", "test_cases": [
                (42, True),
                (42.0, False),
                ("42", False),
                (True, False)  # bool is not int in isinstance check
            ]},
            {"type_name": "str", "test_cases": [
                ("hello", True),
                ("", True),
                (42, False),
                (None, False)
            ]},
            {"type_name": "list", "test_cases": [
                ([1, 2, 3], True),
                ([], True),
                ((1, 2, 3), False),
                ("123", False)
            ]},
            {"type_name": "dict", "test_cases": [
                ({"a": 1}, True),
                ({}, True),
                ([("a", 1)], False),
                ("dict", False)
            ]},
            # Built-in types by type object
            {"type_name": float, "test_cases": [
                (3.14, True),
                (42.0, True),
                (42, False),
                ("3.14", False)
            ]},
            {"type_name": bool, "test_cases": [
                (True, True),
                (False, True),
                (1, False),  # int is not bool
                ("True", False)
            ]},
            # Custom classes
            {"type_name": "CustomClass", "test_cases": [
                (CustomClass(), True),
                (ChildClass(), False),  # String name doesn't work with inheritance for local classes
                ("CustomClass", False),
                (42, False)
            ]},
            {"type_name": CustomClass, "test_cases": [
                (CustomClass(), True),
                (ChildClass(), True),  # Inheritance
                ("CustomClass", False),
                (42, False)
            ]}
        ]
        
        for case in test_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(type_name=case["type_name"], value=type(test_value).__name__):
                    config = ExpectConfig(assertion="is_instance_of", value=case["type_name"])
                    assertion = IsInstanceOfAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)

    def test_raises_exception_assertion_comprehensive(self):
        test_cases = [
            # Built-in exceptions by string name
            {"exception_name": "ValueError", "test_cases": [
                (ValueError("test"), True),
                (ValueError(), True),
                (TypeError("test"), False),
                (RuntimeError("test"), False),
                ("ValueError", False),  # Not an exception
                (42, False)
            ]},
            {"exception_name": "TypeError", "test_cases": [
                (TypeError("test"), True),
                (ValueError("test"), False),
                (Exception("test"), False)  # Parent class doesn't match
            ]},
            # Built-in exceptions by type object
            {"exception_name": RuntimeError, "test_cases": [
                (RuntimeError("test"), True),
                (ValueError("test"), False),
                ("RuntimeError", False)
            ]},
            # Exception inheritance
            {"exception_name": Exception, "test_cases": [
                (ValueError("test"), True),  # ValueError inherits from Exception
                (RuntimeError("test"), True),  # RuntimeError inherits from Exception
                (TypeError("test"), True),   # TypeError inherits from Exception
                ("Exception", False),
                (42, False)
            ]},
            # Custom exceptions
            {"exception_name": "CustomError", "test_cases": [
                (type("CustomError", (Exception,), {})("test"), True),
                (ValueError("test"), False)
            ]}
        ]
        
        for case in test_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(exception_name=case["exception_name"], value=type(test_value).__name__):
                    config = ExpectConfig(assertion="raises_exception", value=case["exception_name"])
                    assertion = RaisesExceptionAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)

    def test_raises_exception_assertion_non_exceptions(self):
        non_exception_cases = [
            {"exception_name": "ValueError", "test_cases": [
                ("not an exception", False),
                (42, False),
                (None, False),
                ([], False),
                ({"error": "ValueError"}, False)
            ]}
        ]
        
        for case in non_exception_cases:
            for test_value, expected_result in case["test_cases"]:
                with self.subTest(exception_name=case["exception_name"], value=test_value):
                    config = ExpectConfig(assertion="raises_exception", value=case["exception_name"])
                    assertion = RaisesExceptionAssertion(config)
                    
                    result = assertion.check(test_value)
                    self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()