import unittest
from pathlib import Path

from src.code_tester.actions_library.io_actions import RunScriptAction
from src.code_tester.config import LogLevel, PerformConfig
from src.code_tester.environment import ExecutionEnvironment
from src.code_tester.exceptions import SolutionImportError
from src.code_tester.output import Console, setup_logging

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestRunScriptAction(unittest.TestCase):
    def setUp(self):
        logger = setup_logging(LogLevel.CRITICAL)
        self.console = Console(logger, is_quiet=True)

    def test_execute_with_stdin_captures_io_correctly(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "single_line_io.py", self.console)
        perform_config = PerformConfig(action="run_script", params={"stdin": "World"})
        action = RunScriptAction(perform_config)

        result = action.execute(env, context={})

        self.assertEqual(result.stdout, "Read: World\n")
        self.assertEqual(result.stderr, "Error\n")
        self.assertIsNone(result.return_value)

    def test_execute_with_multiline_stdin(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "multi_line_io.py", self.console)
        perform_config = PerformConfig(action="run_script", params={"stdin": "first\nsecond"})
        action = RunScriptAction(perform_config)

        result = action.execute(env, context={})

        self.assertEqual(result.stdout, "first-second\n")
        self.assertEqual(result.stderr, "")

    def test_execute_with_empty_params_dict(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "single_line_io.py", self.console)
        perform_config = PerformConfig(action="run_script", params={})
        action = RunScriptAction(perform_config)

        with self.assertRaises(SolutionImportError) as cm:
            action.execute(env, context={})

        self.assertIsInstance(cm.exception.__cause__, EOFError)

    def test_execute_with_null_params(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "single_line_io.py", self.console)
        perform_config = PerformConfig(action="run_script", params=None)
        action = RunScriptAction(perform_config)

        with self.assertRaises(SolutionImportError) as cm:
            action.execute(env, context={})

        self.assertIsInstance(cm.exception.__cause__, EOFError)

    def test_execute_returns_empty_result_for_non_io_script(self):
        no_io_script = FIXTURES_DIR / "no_io.py"
        no_io_script.write_text("a = 1 + 1", encoding="utf-8")

        env = ExecutionEnvironment(no_io_script, self.console)
        perform_config = PerformConfig(action="run_script")
        action = RunScriptAction(perform_config)

        result = action.execute(env, context={})

        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

        no_io_script.unlink()
