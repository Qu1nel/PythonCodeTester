import unittest
from unittest.mock import patch

from src.code_tester.cli import setup_arg_parser
from src.code_tester.config import LogLevel


class TestCli(unittest.TestCase):
    def setUp(self):
        self.parser = setup_arg_parser()

    def test_parses_required_args_correctly(self):
        args = self.parser.parse_args(["solution.py", "test_case.json"])
        self.assertEqual(str(args.solution_path), "solution.py")
        self.assertEqual(str(args.test_case_path), "test_case.json")

    def test_parses_log_level_correctly(self):
        args_upper = self.parser.parse_args(["s.py", "r.json", "--log", "DEBUG"])
        self.assertEqual(args_upper.log, LogLevel.DEBUG)

        args_lower = self.parser.parse_args(["s.py", "r.json", "--log", "info"])
        self.assertEqual(args_lower.log, LogLevel.INFO)

    def test_parses_all_flags_correctly(self):
        cmd_args = ["s.py", "r.json", "--quiet", "--exit-on-first-error", "--no-verdict", "--max-messages", "10"]
        args = self.parser.parse_args(cmd_args)

        self.assertTrue(args.quiet)
        self.assertTrue(args.exit_on_first_error)
        self.assertTrue(args.no_verdict)
        self.assertEqual(args.max_messages, 10)

    def test_default_values_are_set(self):
        args = self.parser.parse_args(["s.py", "r.json"])

        self.assertEqual(args.log, LogLevel.ERROR)
        self.assertFalse(args.quiet)
        self.assertFalse(args.no_verdict)
        self.assertFalse(args.exit_on_first_error)
        self.assertEqual(args.max_messages, 0)

    def test_parser_exits_on_missing_args(self):
        with self.assertRaises(SystemExit):
            with patch("sys.stderr"):
                self.parser.parse_args(["solution.py"])

    def test_parser_exits_on_invalid_choice(self):
        with self.assertRaises(SystemExit):
            with patch("sys.stderr"):
                self.parser.parse_args(["s.py", "r.json", "--log", "INVALID_LEVEL"])

    def test_version_flag_exits(self):
        with self.assertRaises(SystemExit) as cm:
            with patch("sys.stdout"):
                self.parser.parse_args(["--version"])
        self.assertEqual(cm.exception.code, 0)
