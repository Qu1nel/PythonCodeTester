import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from code_tester.config import AppConfig, TestCaseConfig
from code_tester.logging import LogLevel, LogConfig, setup_logger, Console
from code_tester.utils import create_dataclass_from_dict


@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_solution_path():
    """Path to sample solution file."""
    return Path("tests/fixtures/solutions/py_general/calculator.py")


@pytest.fixture
def sample_test_case_path():
    """Path to sample test case file."""
    return Path("tests/fixtures/test_cases/py_general/calculator_test.json")


@pytest.fixture
def app_config(sample_solution_path, sample_test_case_path):
    """Sample AppConfig for testing."""
    return AppConfig(
        solution_path=sample_solution_path,
        test_case_path=sample_test_case_path,
        log_level=LogLevel.DEBUG,
        max_messages=10
    )


@pytest.fixture
def test_case_config(sample_test_case_path):
    """Sample TestCaseConfig for testing."""
    import json
    raw_data = json.loads(sample_test_case_path.read_text("utf-8"))
    return create_dataclass_from_dict(TestCaseConfig, raw_data)


@pytest.fixture
def logger():
    """Logger instance for testing."""
    log_config = LogConfig(
        level=LogLevel.DEBUG,
        console_enabled=False
    )
    return setup_logger(log_config)


@pytest.fixture
def console(logger):
    """Console instance for testing."""
    return Console(logger, is_quiet=True)


@pytest.fixture
def fixtures_dir():
    """Path to fixtures directory."""
    return Path("tests/fixtures")


@pytest.fixture
def solutions_dir(fixtures_dir):
    """Path to solutions fixtures directory."""
    return fixtures_dir / "solutions"


@pytest.fixture
def test_cases_dir(fixtures_dir):
    """Path to test cases fixtures directory."""
    return fixtures_dir / "test_cases"


@pytest.fixture
def py_general_solutions(solutions_dir):
    """Path to py_general solutions."""
    return solutions_dir / "py_general"


@pytest.fixture
def api_solutions(solutions_dir):
    """Path to api solutions."""
    return solutions_dir / "api"


@pytest.fixture
def flask_solutions(solutions_dir):
    """Path to flask solutions."""
    return solutions_dir / "flask"


@pytest.fixture
def arcade_solutions(solutions_dir):
    """Path to arcade solutions."""
    return solutions_dir / "arcade"