import logging
import unittest
from unittest.mock import MagicMock, patch

from src.code_tester.config import LogLevel
from src.code_tester.output import TRACE_LEVEL_NUM, Console, log_initialization, setup_logging


class TestSetupLogging(unittest.TestCase):
    def test_trace_level_is_added(self):
        self.assertEqual(logging.getLevelName("TRACE"), TRACE_LEVEL_NUM)

    def test_setup_logging_configures_root_logger(self):
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers[:]
        original_level = root_logger.level

        try:
            logger = setup_logging(LogLevel.DEBUG)

            self.assertIs(logger, root_logger)
            self.assertEqual(root_logger.level, logging.DEBUG)
            self.assertEqual(len(root_logger.handlers), 1)
            # noinspection PyTypeChecker
            self.assertIsInstance(root_logger.handlers[0], logging.StreamHandler)
        finally:
            root_logger.handlers = original_handlers
            root_logger.setLevel(original_level)


class TestLogInitializationDecorator(unittest.TestCase):
    @patch("logging.getLogger")
    def test_decorator_logs_start_and_end_messages(self, mock_get_logger):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        class MyTestClass:
            @log_initialization(level=LogLevel.INFO)
            def __init__(self, x: int):
                self.x = x

        MyTestClass(10)

        self.assertEqual(mock_logger.log.call_count, 2)
        first_call_args = mock_logger.log.call_args_list[0].args
        second_call_args = mock_logger.log.call_args_list[1].args

        self.assertIn("Initializing MyTestClass...", first_call_args)
        self.assertIn("MyTestClass initialized.", second_call_args)


class TestConsole(unittest.TestCase):
    def setUp(self):
        self.mock_logger = MagicMock()
        self.console_normal = Console(self.mock_logger, is_quiet=False, show_verdict=True)
        self.console_quiet = Console(self.mock_logger, is_quiet=True, show_verdict=True)
        self.console_no_verdict = Console(self.mock_logger, is_quiet=False, show_verdict=False)

    def test_should_print_logic(self):
        self.assertTrue(self.console_normal.should_print(is_verdict=False, show_user=True))
        self.assertFalse(self.console_normal.should_print(is_verdict=False, show_user=False))
        self.assertTrue(self.console_normal.should_print(is_verdict=True, show_user=False))

        self.assertFalse(self.console_quiet.should_print(is_verdict=False, show_user=True))
        self.assertFalse(self.console_quiet.should_print(is_verdict=True, show_user=True))

        self.assertTrue(self.console_no_verdict.should_print(is_verdict=False, show_user=True))
        self.assertFalse(self.console_no_verdict.should_print(is_verdict=True, show_user=True))

    @patch("builtins.print")
    def test_print_calls_logger_and_stdout_when_allowed(self, mock_print):
        self.console_normal.print("hello", level=LogLevel.INFO, show_user=True)

        self.mock_logger.log.assert_called_once()
        mock_print.assert_called_once_with("hello", file=self.console_normal._stdout)

    @patch("builtins.print")
    def test_print_calls_only_logger_when_disallowed(self, mock_print):
        self.console_normal.print("hello", level=LogLevel.INFO, show_user=False)

        self.mock_logger.log.assert_called_once()
        mock_print.assert_not_called()

    def test_print_uses_correct_log_level(self):
        self.console_normal.print("debug message", level="DEBUG")
        self.mock_logger.log.assert_called_with(logging.DEBUG, "debug message", stacklevel=2, exc_info=False)

        self.console_normal.print("critical message", level=LogLevel.CRITICAL)
        self.mock_logger.log.assert_called_with(logging.CRITICAL, "critical message", stacklevel=2, exc_info=False)

    def test_print_handles_exc_info(self):
        self.console_normal.print("error message", level="ERROR", exc_info=True)
        self.mock_logger.log.assert_called_with(logging.ERROR, "error message", stacklevel=2, exc_info=True)
