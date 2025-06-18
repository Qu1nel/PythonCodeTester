"""A flexible framework for dynamic testing of Python code.

This package provides a comprehensive toolkit for executing Python source code
in a controlled environment and verifying its behavior against a declarative
set of test scenarios defined in a JSON format.

The primary entry point for using this package programmatically is the
`DynamicTester` class.

Example:
    A minimal example of using the tester as a library.

    .. code-block:: python

        from code_tester import DynamicTester, AppConfig, LogLevel
        from code_tester.output import Console, setup_logging
        from pathlib import Path

        # Basic setup
        logger = setup_logging(LogLevel.INFO)
        console = Console(logger)
        config = AppConfig(
            solution_path=Path("path/to/solution.py"),
            test_case_path=Path("path/to/test_case.json"),
            log_level=LogLevel.INFO,
            is_silent=False,
            stop_on_first_fail=False
        )

        # Run tests
        tester = DynamicTester(config, console)
        tests_passed = tester.run()

        if tests_passed:
            print("All tests passed!")

Attributes:
    __version__ (str): The current version of the package.
    __all__ (list[str]): The list of public objects exposed by the package.
"""

from .config import AppConfig, ExitCode, LogLevel

from .core import DynamicTester
from .exceptions import TestCaseError, TestCheckError

__all__ = [
    "DynamicTester",
    "AppConfig",
    "ExitCode",
    "LogLevel",
    "TestCaseError",
    "TestCheckError",
]

__version__ = "0.1.0"