import pytest
from pathlib import Path

from code_tester.utils.exceptions import (
    CodeTesterError,
    ExecutionError,
    ConfigError,
    TestCaseParsingError,
    SolutionImportError,
    ActionError,
    ValidationError,
    PluginError,
    AssertionError as CodeTesterAssertionError
)


class TestExceptions:
    def test_code_tester_error_is_base(self):
        error = CodeTesterError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_execution_error_inheritance(self):
        error = ExecutionError("Execution failed")
        assert isinstance(error, CodeTesterError)
        assert str(error) == "Execution failed"

    def test_config_error_with_path(self):
        path = Path("test.json")
        error = ConfigError("Invalid config", path=path)
        
        assert isinstance(error, CodeTesterError)
        assert str(path) in str(error)
        assert "Invalid config" in str(error)
        assert error.path == path

    def test_test_case_parsing_error_with_check_id(self):
        path = Path("test.json")
        error = TestCaseParsingError("Missing field", path=path, check_id=5)
        
        assert isinstance(error, ConfigError)
        assert "check '5'" in str(error)
        assert "Missing field" in str(error)
        assert error.check_id == 5

    def test_test_case_parsing_error_without_check_id(self):
        path = Path("test.json")
        error = TestCaseParsingError("Invalid JSON", path=path)
        
        assert isinstance(error, ConfigError)
        assert "Invalid JSON" in str(error)
        assert error.check_id is None

    def test_solution_import_error(self):
        path = Path("solution.py")
        error = SolutionImportError("Syntax error", path=path)
        
        assert isinstance(error, ExecutionError)
        assert "Failed to import solution file" in str(error)
        assert str(path) in str(error)
        assert error.path == path

    def test_action_error(self):
        error = ActionError("Function not found", check_id=3, action="call_function")
        
        assert isinstance(error, ExecutionError)
        assert "action 'call_function'" in str(error)
        assert "check '3'" in str(error)
        assert error.check_id == 3
        assert error.action == "call_function"

    def test_validation_error(self):
        error = ValidationError("Schema validation failed")
        assert isinstance(error, CodeTesterError)
        assert str(error) == "Schema validation failed"

    def test_plugin_error(self):
        error = PluginError("Plugin loading failed")
        assert isinstance(error, CodeTesterError)
        assert str(error) == "Plugin loading failed"

    def test_assertion_error_renamed(self):
        error = CodeTesterAssertionError("Assertion failed")
        assert isinstance(error, ExecutionError)
        assert str(error) == "Assertion failed"