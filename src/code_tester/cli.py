"""Defines the command-line interface for the code tester.

This module is responsible for parsing command-line arguments, setting up the
application configuration, and orchestrating the main dynamic testing workflow.
It acts as the primary entry point for user interaction.
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import AppConfig, ExitCode, LogLevel
from .core import DynamicTester
from .exceptions import CodeTesterError
from .output import Console, setup_logging


def setup_arg_parser() -> argparse.ArgumentParser:
    """Creates and configures the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="testing-cod",
        description="Executes a Python solution against a dynamic test case.",
    )
    parser.add_argument("solution_path", type=Path, help="Path to the Python solution file to test.")
    parser.add_argument("test_case_path", type=Path, help="Path to the JSON file with the test case.")
    parser.add_argument(
        "-l",
        "--log-level",
        type=LogLevel,
        choices=list(LogLevel),
        default=LogLevel.WARNING,
        help="Set the logging level (default: WARNING).",
    )
    parser.add_argument("--silent", action="store_true", help="Suppress stdout output, show only logs.")
    parser.add_argument("--stop-on-first-fail", action="store_true", help="Stop after the first failed check.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def run_from_cli() -> None:
    """Runs the full application lifecycle from the command line."""
    parser = setup_arg_parser()
    args = parser.parse_args()

    logger = setup_logging(args.log_level)
    console = Console(logger, is_silent=args.silent)
    config = AppConfig(
        solution_path=args.solution_path,
        test_case_path=args.test_case_path,
        log_level=args.log_level,
        is_silent=args.silent,
        stop_on_first_fail=args.stop_on_first_fail,
    )

    try:
        console.print(f"Starting test run for: {config.solution_path}", level=LogLevel.INFO)

        tester = DynamicTester(config, console)
        all_passed = tester.run()

        if all_passed:
            console.print("All tests passed.", level=LogLevel.INFO)
            sys.exit(ExitCode.SUCCESS)
        else:
            console.print("Some tests failed.", level=LogLevel.ERROR)
            sys.exit(ExitCode.TESTS_FAILED)

    except CodeTesterError as e:
        console.print(str(e), level=LogLevel.CRITICAL)
        sys.exit(ExitCode.TESTS_FAILED)
    except FileNotFoundError as e:
        console.print(f"Error: File not found - {e.strerror}: {e.filename}", level=LogLevel.CRITICAL)
        sys.exit(ExitCode.FILE_NOT_FOUND)
    except Exception as e:
        console.print(f"An unexpected error occurred: {e}", level=LogLevel.CRITICAL)
        logger.exception("Traceback for unexpected error:")
        sys.exit(ExitCode.UNEXPECTED_ERROR)
