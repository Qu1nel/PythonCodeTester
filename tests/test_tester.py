import unittest
from pathlib import Path

from src.code_tester.actions_library.io_actions import RunScriptAction
from src.code_tester.config import AppConfig, LogLevel, PerformConfig
from src.code_tester.tester import DynamicTester
from src.code_tester.environment import ExecutionEnvironment
from src.code_tester.output import Console, setup_logging

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestDynamicTesterIntegration(unittest.TestCase):
    def setUp(self):
        logger = setup_logging(LogLevel.CRITICAL)
        self.console = Console(logger, is_quiet=True)

    def run_tester(self, solution_file: Path, test_case_file: Path) -> bool:
        config = AppConfig(
            solution_path=solution_file,
            test_case_path=test_case_file,
            log_level=LogLevel.TRACE,
            is_quiet=False,
            exit_on_first_error=False,
            max_messages=0,
        )
        tester = DynamicTester(config, self.console)
        return tester.run()

    def test_passing_scenario(self):
        result = self.run_tester(FIXTURES_DIR / "simple_script.py", FIXTURES_DIR / "t01_simple_pass.json")
        self.assertTrue(result, "A correct script and test should result in a pass.")

    def test_execute_returns_empty_result_for_non_io_script(self):
        no_io_script_path = FIXTURES_DIR / "no_io.py"
        no_io_script_path.write_text("a = 1 + 1", encoding="utf-8")

        env = ExecutionEnvironment(no_io_script_path, self.console)
        perform_config = PerformConfig(action="run_script")
        action = RunScriptAction(perform_config)

        result = action.execute(env, context={})

        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_random_input_random_output(self):
        random_output_script_path = FIXTURES_DIR / "random_output.py"

        env = ExecutionEnvironment(random_output_script_path, self.console)
        perform_config = PerformConfig(action="run_script")
        action = RunScriptAction(perform_config)

        result = action.execute(env, context={})

        self.assertEqual(result.stderr, "")
        self.assertNotEqual(result.stdout, "")
        self.assertTrue(result.stdout.strip().isnumeric())

    def test_stab_arcade(self):
        no_io_script_path = FIXTURES_DIR / "stab_arcade.py"

        env = ExecutionEnvironment(no_io_script_path, self.console)
        perform_config = PerformConfig(action="run_script")
        action = RunScriptAction(perform_config)

        result = action.execute(env, context={})

        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
