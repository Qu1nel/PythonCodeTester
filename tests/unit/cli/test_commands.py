import pytest
from pathlib import Path
from typer.testing import CliRunner

from code_tester.cli.commands import app


class TestCLICommands:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help_command(self):
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Dynamic testing framework" in result.stdout
        assert "run" in result.stdout
        assert "validate" in result.stdout
        assert "init" in result.stdout

    def test_run_command_help(self):
        result = self.runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "Execute a Python solution" in result.stdout
        assert "solution_path" in result.stdout
        assert "test_case_path" in result.stdout

    def test_validate_command_help(self):
        result = self.runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate a test case JSON file" in result.stdout

    def test_init_command_help(self):
        result = self.runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize a new test project" in result.stdout

    def test_run_missing_arguments(self):
        result = self.runner.invoke(app, ["run"])
        assert result.exit_code != 0

    def test_run_nonexistent_file(self):
        result = self.runner.invoke(app, ["run", "nonexistent.py", "nonexistent.json"])
        assert result.exit_code != 0

    def test_validate_nonexistent_file(self):
        result = self.runner.invoke(app, ["validate", "nonexistent.json"])
        assert result.exit_code != 0

    def test_init_creates_project_structure(self, tmp_path):
        project_name = "test-project"
        result = self.runner.invoke(app, ["init", project_name, "--output", str(tmp_path)])
        
        assert result.exit_code == 0
        assert "Project initialized!" in result.stdout
        
        project_path = tmp_path / project_name
        assert project_path.exists()
        assert (project_path / "solutions").exists()
        assert (project_path / "test_cases").exists()
        assert (project_path / "solutions" / "sample_solution.py").exists()
        assert (project_path / "test_cases" / "sample_test.json").exists()
        assert (project_path / "README.md").exists()

    def test_init_existing_directory_fails(self, tmp_path):
        project_name = "existing-project"
        project_path = tmp_path / project_name
        project_path.mkdir()
        
        result = self.runner.invoke(app, ["init", project_name, "--output", str(tmp_path)])
        assert result.exit_code == 1
        assert "already exists" in result.stdout