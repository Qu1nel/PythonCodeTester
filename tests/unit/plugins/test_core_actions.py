import unittest
from pathlib import Path
from unittest.mock import Mock

from code_tester.config import PerformConfig
from code_tester.execution import ExecutionEnvironment
from code_tester.logging import LogConfig, LogLevel, setup_logger, Console
from code_tester.plugins.core_actions import (
    CallFunctionAction,
    CallMethodAction,
    CreateObjectAction,
    GetAttributeAction,
    ReadFileContentAction,
    RunScriptAction,
)

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "solutions" / "py_general"


class TestRunScriptAction(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_run_script_with_stdin(self):
        config = PerformConfig(action="run_script", params={"stdin": "World"})
        action = RunScriptAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_script.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertEqual(result.stdout.strip(), "Hello, World!")
        self.assertEqual(result.stderr, "")

    def test_run_script_with_save_as(self):
        config = PerformConfig(action="run_script", params={"stdin": "Test"}, save_as="test_module")
        action = RunScriptAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_script.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertIn("test_module", context)
        self.assertIsNotNone(context["test_module"])


class TestCallFunctionAction(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_call_function_with_args(self):
        config = PerformConfig(
            action="call_function",
            target="add",
            params={"args": [2, 3]}
        )
        action = CallFunctionAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_functions.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertEqual(result.return_value, 5)
        self.assertIsNone(result.exception)

    def test_call_function_with_kwargs(self):
        config = PerformConfig(
            action="call_function",
            target="greet",
            params={"args": ["Alice"], "kwargs": {"greeting": "Hi"}}
        )
        action = CallFunctionAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_functions.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertEqual(result.return_value, "Hi, Alice!")

    def test_call_function_with_exception(self):
        config = PerformConfig(
            action="call_function",
            target="divide",
            params={"args": [10, 0]}
        )
        action = CallFunctionAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_functions.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertIsInstance(result.exception, ValueError)
        self.assertIn("Cannot divide by zero", str(result.exception))

    def test_call_nonexistent_function(self):
        config = PerformConfig(
            action="call_function",
            target="nonexistent",
            params={"args": []}
        )
        action = CallFunctionAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_functions.py", self.console)
        context = {}

        with self.assertRaises(AttributeError):
            action.execute(env, context)

    def test_call_function_with_save_as(self):
        config = PerformConfig(
            action="call_function",
            target="add",
            params={"args": [5, 7]},
            save_as="result"
        )
        action = CallFunctionAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_functions.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertEqual(result.return_value, 12)
        self.assertEqual(context["result"], 12)


class TestCreateObjectAction(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_create_object_no_args(self):
        config = PerformConfig(
            action="create_object",
            target="Calculator"
        )
        action = CreateObjectAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertIsNotNone(result.return_value)
        self.assertEqual(result.return_value.value, 0)

    def test_create_object_with_args(self):
        config = PerformConfig(
            action="create_object",
            target="Calculator",
            params={"args": [10]}
        )
        action = CreateObjectAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertIsNotNone(result.return_value)
        self.assertEqual(result.return_value.value, 10)

    def test_create_object_with_kwargs(self):
        config = PerformConfig(
            action="create_object",
            target="Person",
            params={"kwargs": {"name": "Alice", "age": 30}}
        )
        action = CreateObjectAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertIsNotNone(result.return_value)
        self.assertEqual(result.return_value.name, "Alice")
        self.assertEqual(result.return_value.age, 30)

    def test_create_object_with_exception(self):
        config = PerformConfig(
            action="create_object",
            target="NonExistentClass"
        )
        action = CreateObjectAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        context = {}

        with self.assertRaises(AttributeError):
            action.execute(env, context)

    def test_create_object_with_save_as(self):
        config = PerformConfig(
            action="create_object",
            target="Calculator",
            save_as="calc"
        )
        action = CreateObjectAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertIn("calc", context)
        self.assertIsNotNone(context["calc"])


class TestCallMethodAction(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_call_method(self):
        config = PerformConfig(
            action="call_method",
            target="add",
            params={"object_ref": "calc", "args": [5]}
        )
        action = CallMethodAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        
        mock_calc = Mock()
        mock_calc.add.return_value = 15
        context = {"calc": mock_calc}

        result = action.execute(env, context)

        self.assertEqual(result.return_value, 15)
        mock_calc.add.assert_called_once_with(5)

    def test_call_method_missing_object(self):
        config = PerformConfig(
            action="call_method",
            target="add",
            params={"object_ref": "missing", "args": [5]}
        )
        action = CallMethodAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        context = {}

        with self.assertRaises(ValueError) as cm:
            action.execute(env, context)
        
        self.assertIn("not found in context", str(cm.exception))

    def test_call_method_missing_method(self):
        config = PerformConfig(
            action="call_method",
            target="nonexistent",
            params={"object_ref": "obj"}
        )
        action = CallMethodAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        context = {"obj": Mock(spec=[])}

        with self.assertRaises(AttributeError):
            action.execute(env, context)


class TestGetAttributeAction(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_get_attribute(self):
        config = PerformConfig(
            action="get_attribute",
            target="name",
            params={"object_ref": "person"}
        )
        action = GetAttributeAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        
        mock_person = Mock()
        mock_person.name = "Alice"
        context = {"person": mock_person}

        result = action.execute(env, context)

        self.assertEqual(result.return_value, "Alice")

    def test_get_attribute_with_save_as(self):
        config = PerformConfig(
            action="get_attribute",
            target="age",
            params={"object_ref": "person"},
            save_as="person_age"
        )
        action = GetAttributeAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_classes.py", self.console)
        
        mock_person = Mock()
        mock_person.age = 25
        context = {"person": mock_person}

        result = action.execute(env, context)

        self.assertEqual(result.return_value, 25)
        self.assertEqual(context["person_age"], 25)


class TestReadFileContentAction(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_read_file_content(self):
        test_file = FIXTURES_DIR.parent.parent / "data" / "test_content.txt"
        
        config = PerformConfig(
            action="read_file_content",
            target=str(test_file)
        )
        action = ReadFileContentAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_script.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertEqual(result.return_value.strip(), "Hello, World!")

    def test_read_file_content_with_encoding(self):
        test_file = FIXTURES_DIR.parent.parent / "data" / "test_content_utf8.txt"
        
        config = PerformConfig(
            action="read_file_content",
            target=str(test_file),
            params={"encoding": "utf-8"}
        )
        action = ReadFileContentAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_script.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertEqual(result.return_value.strip(), "Привет, мир!")

    def test_read_nonexistent_file(self):
        config = PerformConfig(
            action="read_file_content",
            target="nonexistent.txt"
        )
        action = ReadFileContentAction(config)
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_script.py", self.console)
        context = {}

        result = action.execute(env, context)

        self.assertIsInstance(result.exception, FileNotFoundError)


if __name__ == '__main__':
    unittest.main()