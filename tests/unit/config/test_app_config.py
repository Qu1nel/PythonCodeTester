import pytest
from pathlib import Path
from pydantic import ValidationError

from code_tester.config import AppConfig
from code_tester.logging import LogLevel


class TestAppConfig:
    def test_valid_config_creation(self):
        config = AppConfig(
            solution_path=Path("tests/fixtures/simple_script.py"),
            test_case_path=Path("tests/fixtures/t01_simple_pass.json"),
            log_level=LogLevel.DEBUG,
            max_messages=5
        )
        
        assert config.solution_path == Path("tests/fixtures/simple_script.py")
        assert config.test_case_path == Path("tests/fixtures/t01_simple_pass.json")
        assert config.log_level == LogLevel.DEBUG
        assert config.max_messages == 5
        assert config.is_quiet is False
        assert config.exit_on_first_error is False

    def test_default_values(self):
        config = AppConfig(
            solution_path=Path("tests/fixtures/simple_script.py"),
            test_case_path=Path("tests/fixtures/t01_simple_pass.json")
        )
        
        assert config.log_level == LogLevel.ERROR
        assert config.is_quiet is False
        assert config.exit_on_first_error is False
        assert config.max_messages == 0

    def test_negative_max_messages_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                solution_path=Path("tests/fixtures/simple_script.py"),
                test_case_path=Path("tests/fixtures/t01_simple_pass.json"),
                max_messages=-1
            )
        
        assert "max_messages must be non-negative" in str(exc_info.value)

    def test_nonexistent_absolute_path_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                solution_path=Path("/nonexistent/file.py").resolve(),
                test_case_path=Path("tests/fixtures/t01_simple_pass.json")
            )
        
        assert "File does not exist" in str(exc_info.value)

    def test_relative_paths_skip_validation(self):
        config = AppConfig(
            solution_path=Path("nonexistent/file.py"),
            test_case_path=Path("nonexistent/test.json")
        )
        
        assert config.solution_path == Path("nonexistent/file.py")
        assert config.test_case_path == Path("nonexistent/test.json")