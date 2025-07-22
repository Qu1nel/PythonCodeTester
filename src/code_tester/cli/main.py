"""Main CLI interface for the code tester."""

import argparse
import sys
from pathlib import Path

from .._version import __version__
from ..config import AppConfig, ExitCode
from ..execution import DynamicTester
from ..utils.exceptions import CodeTesterError
from ..logging import LogConfig, LogLevel, setup_logger, Console, generate_trace_id, set_trace_id


def log_level_type(value: str) -> LogLevel:
    """Convert string to LogLevel enum.
    
    Args:
        value: String representation of log level
        
    Returns:
        LogLevel enum value
        
    Raises:
        argparse.ArgumentTypeError: If value is not a valid log level
    """
    try:
        return LogLevel(value.upper())
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid log level. Choose from: {', '.join(LogLevel)}")


def setup_arg_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="run-test-case",
        description="Executes a Python solution against a dynamic test case.",
    )
    parser.add_argument("solution_path", type=Path, help="Path to the Python solution file to test.")
    parser.add_argument("test_case_path", type=Path, help="Path to the JSON file with the test case.")

    parser.add_argument(
        "--log",
        type=log_level_type,
        default=LogLevel.ERROR,
        help="Set the logging level for stderr (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: ERROR.",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress all stdout output (test results and final verdict)."
    )
    parser.add_argument("--no-verdict", action="store_true", help="Suppress final verdict, show only failed checks.")
    parser.add_argument(
        "--max-messages",
        type=int,
        default=0,
        metavar="N",
        help="Maximum number of failed check messages to display (0 for no limit).",
    )
    parser.add_argument(
        "-x", "--exit-on-first-error", action="store_true", help="Exit instantly on the first failed check."
    )
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")
    return parser


def run_from_cli() -> None:
    """Main CLI entry point."""
    parser = setup_arg_parser()
    args = parser.parse_args()

    # Setup new logging system
    log_config = LogConfig(
        level=args.log,
        console_enabled=True,
        colorize=not args.quiet
    )
    logger = setup_logger(log_config)
    console = Console(logger, is_quiet=args.quiet, show_verdict=not args.no_verdict)
    
    # Generate trace ID for this test run
    trace_id = generate_trace_id()
    set_trace_id(trace_id)
    
    console.print(f"Logger configured with level: {args.log}", level=LogLevel.DEBUG)

    config = AppConfig(
        solution_path=args.solution_path,
        test_case_path=args.test_case_path,
        log_level=args.log,
        is_quiet=args.quiet,
        exit_on_first_error=args.exit_on_first_error,
        max_messages=args.max_messages,
    )
    console.print(f"Tester config: {config}", level=LogLevel.TRACE)

    try:
        console.print(f"Starting test run for: {config.solution_path}", level=LogLevel.INFO, show_user=True)

        tester = DynamicTester(config, console)

        console.print("Running test case...", level=LogLevel.TRACE)
        all_passed = tester.run()
        console.print(f"Test case finished. Overall result: {all_passed}", level=LogLevel.TRACE)

        if all_passed:
            console.print("✅ All tests passed.", level=LogLevel.INFO, is_verdict=True)
            sys.exit(ExitCode.SUCCESS)
        else:
            console.print(
                f"❌ Some tests failed. ({len(tester.failed_checks_ids)} of {len(tester.test_case_config.checks)})",
                level=LogLevel.WARNING,
                is_verdict=True,
            )
            sys.exit(ExitCode.TESTS_FAILED)

    except CodeTesterError as e:
        console.print(
            f"Error: A tester framework error occurred: {e}", level=LogLevel.CRITICAL, show_user=True, exc_info=True
        )
        sys.exit(ExitCode.TESTS_FAILED)
    except FileNotFoundError as e:
        console.print(f"Error: Input file not found: {e.filename}", level=LogLevel.CRITICAL, show_user=True)
        sys.exit(ExitCode.FILE_NOT_FOUND)
    except Exception as e:
        console.print(
            f"Error: An unexpected error occurred: {e.__class__.__name__}. See logs for detailed traceback.",
            level=LogLevel.CRITICAL,
            show_user=True,
            exc_info=True,
        )
        sys.exit(ExitCode.UNEXPECTED_ERROR)