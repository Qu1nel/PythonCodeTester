import unittest

from src.code_tester.config import ExpectConfig
from src.code_tester.plugins.core_assertions import (
    ContainsAssertion,
    EqualsAssertion,
    IsCloseToAssertion,
    IsInRangeAssertion,
    IsInstanceOfAssertion,
    RaisesExceptionAssertion,
)


class TestEqualsAssertion(unittest.TestCase):
    def test_equals_numbers(self):
        config = ExpectConfig(assertion="equals", value=42)
        assertion = EqualsAssertion(config)

        self.assertTrue(assertion.check(42))
        self.assertFalse(assertion.check(43))

    def test_equals_strings(self):
        config = ExpectConfig(assertion="equals", value="hello")
        assertion = EqualsAssertion(config)

        self.assertTrue(assertion.check("hello"))
        self.assertTrue(assertion.check("  hello  "))
        self.assertFalse(assertion.check("Hello"))

    def test_equals_lists(self):
        config = ExpectConfig(assertion="equals", value=[1, 2, 3])
        assertion = EqualsAssertion(config)

        self.assertTrue(assertion.check([1, 2, 3]))
        self.assertFalse(assertion.check([3, 2, 1]))

    def test_equals_none(self):
        config = ExpectConfig(assertion="equals", value=None)
        assertion = EqualsAssertion(config)

        self.assertTrue(assertion.check(None))
        self.assertFalse(assertion.check(0))


class TestContainsAssertion(unittest.TestCase):
    def test_contains_string(self):
        config = ExpectConfig(assertion="contains", value="world")
        assertion = ContainsAssertion(config)

        self.assertTrue(assertion.check("hello world"))
        self.assertFalse(assertion.check("hello earth"))

    def test_contains_list(self):
        config = ExpectConfig(assertion="contains", value=2)
        assertion = ContainsAssertion(config)

        self.assertTrue(assertion.check([1, 2, 3]))
        self.assertFalse(assertion.check([1, 3, 4]))

    def test_contains_tuple(self):
        config = ExpectConfig(assertion="contains", value="b")
        assertion = ContainsAssertion(config)

        self.assertTrue(assertion.check(("a", "b", "c")))
        self.assertFalse(assertion.check(("a", "c", "d")))

    def test_contains_dict(self):
        config = ExpectConfig(assertion="contains", value="key1")
        assertion = ContainsAssertion(config)

        self.assertTrue(assertion.check({"key1": "value1", "key2": "value2"}))
        self.assertFalse(assertion.check({"key2": "value2", "key3": "value3"}))

    def test_contains_unsupported_type(self):
        config = ExpectConfig(assertion="contains", value="test")
        assertion = ContainsAssertion(config)

        self.assertFalse(assertion.check(42))
        self.assertFalse(assertion.check(None))


class TestIsInRangeAssertion(unittest.TestCase):
    def test_is_in_range_valid(self):
        config = ExpectConfig(assertion="is_in_range", value={"min": 1, "max": 10})
        assertion = IsInRangeAssertion(config)

        self.assertTrue(assertion.check(5))
        self.assertTrue(assertion.check(1))
        self.assertTrue(assertion.check(10))
        self.assertTrue(assertion.check(5.5))

    def test_is_in_range_outside(self):
        config = ExpectConfig(assertion="is_in_range", value={"min": 1, "max": 10})
        assertion = IsInRangeAssertion(config)

        self.assertFalse(assertion.check(0))
        self.assertFalse(assertion.check(11))
        self.assertFalse(assertion.check(-5))

    def test_is_in_range_non_numeric(self):
        config = ExpectConfig(assertion="is_in_range", value={"min": 1, "max": 10})
        assertion = IsInRangeAssertion(config)

        self.assertFalse(assertion.check("5"))
        self.assertFalse(assertion.check(None))
        self.assertFalse(assertion.check([5]))

    def test_is_in_range_invalid_config(self):
        config = ExpectConfig(assertion="is_in_range", value={"min": 1})
        assertion = IsInRangeAssertion(config)

        self.assertFalse(assertion.check(5))

        config = ExpectConfig(assertion="is_in_range", value="invalid")
        assertion = IsInRangeAssertion(config)

        self.assertFalse(assertion.check(5))


class TestIsCloseToAssertion(unittest.TestCase):
    def test_is_close_to_default_tolerance(self):
        config = ExpectConfig(assertion="is_close_to", value=3.14159)
        assertion = IsCloseToAssertion(config)

        self.assertTrue(assertion.check(3.14159))
        self.assertTrue(assertion.check(3.141590000000001))
        self.assertFalse(assertion.check(3.15))

    def test_is_close_to_custom_tolerance(self):
        config = ExpectConfig(assertion="is_close_to", value=10.0, tolerance=0.1)
        assertion = IsCloseToAssertion(config)

        self.assertTrue(assertion.check(10.05))
        self.assertTrue(assertion.check(9.95))
        self.assertFalse(assertion.check(10.2))

    def test_is_close_to_integers(self):
        config = ExpectConfig(assertion="is_close_to", value=100, tolerance=5)
        assertion = IsCloseToAssertion(config)

        self.assertTrue(assertion.check(102))
        self.assertTrue(assertion.check(98))
        self.assertFalse(assertion.check(106))

    def test_is_close_to_non_numeric(self):
        config = ExpectConfig(assertion="is_close_to", value=3.14)
        assertion = IsCloseToAssertion(config)

        self.assertFalse(assertion.check("3.14"))
        self.assertFalse(assertion.check(None))
        self.assertFalse(assertion.check([3.14]))


class TestIsInstanceOfAssertion(unittest.TestCase):
    def test_is_instance_of_string_type_name(self):
        config = ExpectConfig(assertion="is_instance_of", value="int")
        assertion = IsInstanceOfAssertion(config)

        self.assertTrue(assertion.check(42))
        self.assertFalse(assertion.check(3.14))
        self.assertFalse(assertion.check("42"))

    def test_is_instance_of_type_object(self):
        config = ExpectConfig(assertion="is_instance_of", value=str)
        assertion = IsInstanceOfAssertion(config)

        self.assertTrue(assertion.check("hello"))
        self.assertFalse(assertion.check(42))

    def test_is_instance_of_custom_class(self):
        class CustomClass:
            pass

        obj = CustomClass()
        config = ExpectConfig(assertion="is_instance_of", value="CustomClass")
        assertion = IsInstanceOfAssertion(config)

        self.assertTrue(assertion.check(obj))
        self.assertFalse(assertion.check("not custom"))

    def test_is_instance_of_inheritance(self):
        class Parent:
            pass

        class Child(Parent):
            pass

        child_obj = Child()
        config = ExpectConfig(assertion="is_instance_of", value=Parent)
        assertion = IsInstanceOfAssertion(config)

        self.assertTrue(assertion.check(child_obj))


class TestRaisesExceptionAssertion(unittest.TestCase):
    def test_raises_exception_string_type_name(self):
        config = ExpectConfig(assertion="raises_exception", value="ValueError")
        assertion = RaisesExceptionAssertion(config)

        self.assertTrue(assertion.check(ValueError("test error")))
        self.assertFalse(assertion.check(TypeError("test error")))
        self.assertFalse(assertion.check("not an exception"))

    def test_raises_exception_type_object(self):
        config = ExpectConfig(assertion="raises_exception", value=RuntimeError)
        assertion = RaisesExceptionAssertion(config)

        self.assertTrue(assertion.check(RuntimeError("test error")))
        self.assertFalse(assertion.check(ValueError("test error")))

    def test_raises_exception_inheritance(self):
        config = ExpectConfig(assertion="raises_exception", value=Exception)
        assertion = RaisesExceptionAssertion(config)

        self.assertTrue(assertion.check(ValueError("test error")))
        self.assertTrue(assertion.check(RuntimeError("test error")))

    def test_raises_exception_non_exception(self):
        config = ExpectConfig(assertion="raises_exception", value="ValueError")
        assertion = RaisesExceptionAssertion(config)

        self.assertFalse(assertion.check("not an exception"))
        self.assertFalse(assertion.check(42))
        self.assertFalse(assertion.check(None))


if __name__ == '__main__':
    unittest.main()