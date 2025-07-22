import sys
import unittest
from pathlib import Path
from types import ModuleType

from code_tester.execution import ExecutionEnvironment
from code_tester.utils.exceptions import SolutionImportError
from code_tester.logging import LogConfig, LogLevel, setup_logger, Console

FIXTURES_DIR = Path(__file__).parent / "env_fixtures"


class TestExecutionEnvironment(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)

    def test_import_solution_module_success(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_io.py", self.console)
        with env.run_in_isolation(stdin_text="dummy"):
            pass

    def test_import_solution_module_fails_for_non_existent_file(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "non_existent.py", self.console)
        with self.assertRaises(FileNotFoundError):
            with env.run_in_isolation():
                pass

    def test_import_solution_module_fails_with_syntax_error(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "syntax_error.py", self.console)
        with self.assertRaises(SolutionImportError) as cm:
            with env.run_in_isolation():
                pass
        self.assertIsInstance(cm.exception.__cause__, SyntaxError)

    def test_import_solution_module_fails_with_runtime_error(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "runtime_error.py", self.console)
        with self.assertRaises(SolutionImportError) as cm:
            with env.run_in_isolation():
                pass
        self.assertIsInstance(cm.exception.__cause__, RuntimeError)

    def test_run_in_isolation_captures_io(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "simple_io.py", self.console)

        with env.run_in_isolation(stdin_text="World") as (module, captured_output):
            self.assertIsInstance(module, ModuleType)

        self.assertIn("Hello, World!", captured_output["stdout"])
        self.assertEqual(captured_output["stderr"].strip(), "Error message")

    def test_module_state_is_isolated_between_runs(self):
        env = ExecutionEnvironment(FIXTURES_DIR / "isolation.py", self.console)

        with env.run_in_isolation() as (module1, _):
            self.assertEqual(module1.COUNTER, 1)
            module1.COUNTER = 99
            module_name_1 = module1.__name__
            self.assertIn(module_name_1, sys.modules)

        self.assertNotIn(module_name_1, sys.modules)

        with env.run_in_isolation() as (module2, _):
            self.assertEqual(module2.COUNTER, 1)
            module_name_2 = module2.__name__

        self.assertNotEqual(module_name_1, module_name_2, "Each run should use a unique module name.")
