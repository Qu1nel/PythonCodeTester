import unittest
from pathlib import Path
from unittest.mock import Mock

from src.code_tester.config import PerformConfig
from src.code_tester.environment import ExecutionEnvironment
from src.code_tester.logging import LogConfig, LogLevel, setup_logger, Console
from src.code_tester.plugins.core_actions import (
    CallFunctionAction,
    CallMethodAction,
    CreateObjectAction,
    GetAttributeAction,
    ReadFileContentAction,
    RunScriptAction,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestAllActionsComprehensive(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_run_script_comprehensive(self):
        test_cases = [
            {
                "name": "simple_io",
                "file": "py_general/simple_io.py",
                "stdin": "Alice\n25",
                "expected_contains": ["Hello, Alice!", "You are 25 years old", "You are an adult"]
            },
            {
                "name": "no_input",
                "file": "py_general/calculator.py",
                "stdin": "",
                "expected_stdout": ""
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                config = PerformConfig(
                    action="run_script",
                    params={"stdin": case["stdin"]} if case["stdin"] else None
                )
                action = RunScriptAction(config)
                env = ExecutionEnvironment(FIXTURES_DIR / case["file"], self.console)
                context = {}

                result = action.execute(env, context)

                if "expected_contains" in case:
                    for expected in case["expected_contains"]:
                        self.assertIn(expected, result.stdout)
                elif "expected_stdout" in case:
                    self.assertEqual(result.stdout, case["expected_stdout"])

    def test_call_function_comprehensive(self):
        test_cases = [
            {
                "name": "factorial_positive",
                "function": "factorial",
                "args": [5],
                "expected": 120
            },
            {
                "name": "fibonacci_sequence",
                "function": "fibonacci",
                "args": [8],
                "expected": 21
            },
            {
                "name": "prime_check_true",
                "function": "is_prime",
                "args": [23],
                "expected": True
            },
            {
                "name": "prime_check_false",
                "function": "is_prime",
                "args": [24],
                "expected": False
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                config = PerformConfig(
                    action="call_function",
                    target=case["function"],
                    params={"args": case["args"]}
                )
                action = CallFunctionAction(config)
                env = ExecutionEnvironment(FIXTURES_DIR / "py_general/calculator.py", self.console)
                context = {}

                result = action.execute(env, context)

                self.assertEqual(result.return_value, case["expected"])
                self.assertIsNone(result.exception)

    def test_call_function_with_exceptions(self):
        exception_cases = [
            {
                "name": "factorial_negative",
                "function": "factorial",
                "args": [-1],
                "expected_exception": ValueError
            },
            {
                "name": "fibonacci_negative",
                "function": "fibonacci",
                "args": [-5],
                "expected_exception": ValueError
            }
        ]
        
        for case in exception_cases:
            with self.subTest(case=case["name"]):
                config = PerformConfig(
                    action="call_function",
                    target=case["function"],
                    params={"args": case["args"]}
                )
                action = CallFunctionAction(config)
                env = ExecutionEnvironment(FIXTURES_DIR / "py_general/calculator.py", self.console)
                context = {}

                result = action.execute(env, context)

                self.assertIsInstance(result.exception, case["expected_exception"])

    def test_create_object_comprehensive(self):
        test_cases = [
            {
                "name": "calculator_default",
                "class": "Calculator",
                "args": [],
                "expected_value": 0.0
            },
            {
                "name": "calculator_with_initial",
                "class": "Calculator",
                "args": [42.5],
                "expected_value": 42.5
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                config = PerformConfig(
                    action="create_object",
                    target=case["class"],
                    params={"args": case["args"]},
                    save_as="test_obj"
                )
                action = CreateObjectAction(config)
                env = ExecutionEnvironment(FIXTURES_DIR / "py_general/calculator.py", self.console)
                context = {}

                result = action.execute(env, context)

                self.assertIsNotNone(result.return_value)
                self.assertEqual(result.return_value.value, case["expected_value"])
                self.assertIn("test_obj", context)

    def test_call_method_comprehensive(self):
        calc_mock = Mock()
        calc_mock.add.return_value = 15.0
        calc_mock.subtract.return_value = 5.0
        calc_mock.multiply.return_value = 50.0
        calc_mock.reset.return_value = None
        
        test_cases = [
            {
                "name": "add_method",
                "method": "add",
                "args": [10.0],
                "expected": 15.0
            },
            {
                "name": "subtract_method",
                "method": "subtract",
                "args": [5.0],
                "expected": 5.0
            },
            {
                "name": "multiply_method",
                "method": "multiply",
                "args": [5.0],
                "expected": 50.0
            },
            {
                "name": "reset_method",
                "method": "reset",
                "args": [],
                "expected": None
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                config = PerformConfig(
                    action="call_method",
                    target=case["method"],
                    params={
                        "object_ref": "calc",
                        "args": case["args"]
                    }
                )
                action = CallMethodAction(config)
                env = ExecutionEnvironment(FIXTURES_DIR / "py_general/calculator.py", self.console)
                context = {"calc": calc_mock}

                result = action.execute(env, context)

                self.assertEqual(result.return_value, case["expected"])

    def test_get_attribute_comprehensive(self):
        mock_obj1 = Mock()
        mock_obj1.name = "Alice"
        mock_obj1.age = 30
        mock_obj1.active = True
        
        mock_obj2 = Mock()
        mock_obj2.value = 42.5
        mock_obj2.count = 100
        mock_obj2.ratio = 0.75
        
        test_objects = [
            {
                "name": "simple_attributes",
                "obj": mock_obj1,
                "attributes": [
                    ("name", "Alice"),
                    ("age", 30),
                    ("active", True)
                ]
            },
            {
                "name": "numeric_attributes",
                "obj": mock_obj2,
                "attributes": [
                    ("value", 42.5),
                    ("count", 100),
                    ("ratio", 0.75)
                ]
            }
        ]
        
        for obj_case in test_objects:
            for attr_name, expected_value in obj_case["attributes"]:
                with self.subTest(case=f"{obj_case['name']}_{attr_name}"):
                    config = PerformConfig(
                        action="get_attribute",
                        target=attr_name,
                        params={"object_ref": "test_obj"},
                        save_as=f"attr_{attr_name}"
                    )
                    action = GetAttributeAction(config)
                    env = ExecutionEnvironment(FIXTURES_DIR / "py_general/calculator.py", self.console)
                    context = {"test_obj": obj_case["obj"]}

                    result = action.execute(env, context)

                    self.assertEqual(result.return_value, expected_value)
                    self.assertEqual(context[f"attr_{attr_name}"], expected_value)

    def test_read_file_content_comprehensive(self):
        test_files = [
            {
                "name": "simple_text",
                "content": "Hello, World!",
                "encoding": "utf-8"
            },
            {
                "name": "multiline_text",
                "content": "Line 1\nLine 2\nLine 3",
                "encoding": "utf-8"
            },
            {
                "name": "unicode_text",
                "content": "Привет, мир! 🌍",
                "encoding": "utf-8"
            },
            {
                "name": "numbers_and_symbols",
                "content": "123 !@# $%^ &*() []{}",
                "encoding": "utf-8"
            }
        ]
        
        for case in test_files:
            with self.subTest(case=case["name"]):
                test_file = FIXTURES_DIR / f"temp_{case['name']}.txt"
                test_file.write_text(case["content"], encoding=case["encoding"])
                
                try:
                    config = PerformConfig(
                        action="read_file_content",
                        target=str(test_file),
                        params={"encoding": case["encoding"]},
                        save_as="file_content"
                    )
                    action = ReadFileContentAction(config)
                    env = ExecutionEnvironment(FIXTURES_DIR / "py_general/calculator.py", self.console)
                    context = {}

                    result = action.execute(env, context)

                    self.assertEqual(result.return_value, case["content"])
                    self.assertEqual(context["file_content"], case["content"])
                    self.assertIsNone(result.exception)
                
                finally:
                    if test_file.exists():
                        test_file.unlink()

    def test_read_file_content_errors(self):
        error_cases = [
            {
                "name": "nonexistent_file",
                "file": "nonexistent_file.txt",
                "expected_exception": FileNotFoundError
            },
            {
                "name": "invalid_encoding",
                "file": "temp_encoding_test.txt",
                "content": "Hello",
                "encoding": "invalid-encoding",
                "expected_exception": LookupError
            }
        ]
        
        for case in error_cases:
            with self.subTest(case=case["name"]):
                if "content" in case:
                    test_file = FIXTURES_DIR / case["file"]
                    test_file.write_text(case["content"], encoding="utf-8")
                
                try:
                    config = PerformConfig(
                        action="read_file_content",
                        target=str(FIXTURES_DIR / case["file"]),
                        params={"encoding": case.get("encoding", "utf-8")}
                    )
                    action = ReadFileContentAction(config)
                    env = ExecutionEnvironment(FIXTURES_DIR / "py_general/calculator.py", self.console)
                    context = {}

                    result = action.execute(env, context)

                    self.assertIsInstance(result.exception, case["expected_exception"])
                
                finally:
                    test_file = FIXTURES_DIR / case["file"]
                    if test_file.exists():
                        test_file.unlink()


if __name__ == '__main__':
    unittest.main()