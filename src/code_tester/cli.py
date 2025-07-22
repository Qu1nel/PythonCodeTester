import argparse
import sys
from pathlib import Path

from . import LogLevel, __version__
from .config import AppConfig, ExitCode
from .tester import DynamicTester, initialize_plugins
from .exceptions import CodeTesterError
from .output import Console, log_level_type, setup_logging


def setup_arg_parser() -> argparse.ArgumentParser:
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
    parser = setup_arg_parser()
    args = parser.parse_args()

    logger = setup_logging(args.log)
    console = Console(logger, is_quiet=args.quiet, show_verdict=not args.no_verdict)
    console.print(f"Logger configured with level: {args.log}", level=LogLevel.DEBUG)
    initialize_plugins(console)

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
