import unittest
from unittest.mock import patch
from typer.testing import CliRunner

from code_tester.cli.commands import app
from code_tester.config import LogLevel


class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_version_command(self):
        result = self.runner.invoke(app, ["run", "--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("version", result.stdout)
        self.assertIn("0.1", result.stdout)

    def test_help_command(self):
        result = self.runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Dynamic testing framework", result.stdout)

    def test_run_command_help(self):
        result = self.runner.invoke(app, ["run", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Execute a Python solution", result.stdout)

    def test_validate_command_help(self):
        result = self.runner.invoke(app, ["validate", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Validate a test case JSON file", result.stdout)

    def test_init_command_help(self):
        result = self.runner.invoke(app, ["init", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Initialize a new test project", result.stdout)

    def test_run_command_missing_args(self):
        result = self.runner.invoke(app, ["run"])
        self.assertNotEqual(result.exit_code, 0)

    def test_validate_command_missing_args(self):
        result = self.runner.invoke(app, ["validate"])
        self.assertNotEqual(result.exit_code, 0)

    def test_init_command_missing_args(self):
        result = self.runner.invoke(app, ["init"])
        self.assertNotEqual(result.exit_code, 0)
