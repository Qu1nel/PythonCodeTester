import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from code_tester.config import CheckConfig, CheckSpec, Expectation, PerformConfig, ExpectConfig
from code_tester.execution import CheckHandler, ExecutionContext, ExecutionEnvironment
from code_tester.logging import LogConfig, LogLevel, setup_logger, Console
from code_tester.plugins.core_actions import ActionResult


class TestCheckHandler(unittest.TestCase):
    def setUp(self):
        log_config = LogConfig(level=LogLevel.CRITICAL, console_enabled=False)
        logger = setup_logger(log_config)
        self.console = Console(logger, is_quiet=True)
        self.check_handler = CheckHandler(self.console)
        self.context = ExecutionContext()
        
        # Mock environment
        self.environment = Mock(spec=ExecutionEnvironment)

    def test_execute_check_success(self):
        # Create a simple check config
        check_config = CheckConfig(
            check_id=1,
            name_for_output="Test check",
            reason_for_output="Should return 5",
            explain_for_error="Check your math",
            spec=CheckSpec(
                perform=PerformConfig(action="call_function", target="add", params={"args": [2, 3]}),
                expect=Expectation(
                    return_value=ExpectConfig(assertion="equals", value=5)
                )
            )
        )
        
        # Mock the action execution
        with patch.object(self.check_handler, '_execute_action') as mock_execute:
            mock_execute.return_value = ActionResult(return_value=5)
            
            result = self.check_handler.execute_check(check_config, self.environment, self.context)
            
            self.assertTrue(result.passed)
            self.assertEqual(result.check_id, 1)
            self.assertIsNone(result.error_message)

    def test_execute_check_failure(self):
        # Create a check config that should fail
        check_config = CheckConfig(
            check_id=2,
            name_for_output="Test check",
            reason_for_output="Expected {expected}, got {actual}",
            explain_for_error="Check your math",
            spec=CheckSpec(
                perform=PerformConfig(action="call_function", target="add", params={"args": [2, 3]}),
                expect=Expectation(
                    return_value=ExpectConfig(assertion="equals", value=10)
                )
            )
        )
        
        # Mock the action execution
        with patch.object(self.check_handler, '_execute_action') as mock_execute:
            mock_execute.return_value = ActionResult(return_value=5)
            
            result = self.check_handler.execute_check(check_config, self.environment, self.context)
            
            self.assertFalse(result.passed)
            self.assertEqual(result.check_id, 2)
            self.assertIn("Expected 10, got 5", result.error_message)

    def test_execute_check_with_exception(self):
        # Create a check config
        check_config = CheckConfig(
            check_id=3,
            name_for_output="Test check",
            reason_for_output="Should handle exception",
            explain_for_error="Check your error handling",
            spec=CheckSpec(
                perform=PerformConfig(action="call_function", target="divide", params={"args": [10, 0]}),
                expect=Expectation(
                    return_value=ExpectConfig(assertion="raises_exception", value="ValueError")
                )
            )
        )
        
        # Mock the action execution with exception
        with patch.object(self.check_handler, '_execute_action') as mock_execute:
            mock_execute.return_value = ActionResult(exception=ValueError("Cannot divide by zero"))
            
            # Mock the assertion check to return True for exception handling
            with patch.object(self.check_handler, '_check_assertion') as mock_assertion:
                mock_assertion.return_value = True
                
                result = self.check_handler.execute_check(check_config, self.environment, self.context)
                
                self.assertTrue(result.passed)
                self.assertEqual(result.check_id, 3)

    def test_execute_check_unexpected_exception(self):
        # Create a check config
        check_config = CheckConfig(
            check_id=4,
            name_for_output="Test check",
            reason_for_output="Should return 5",
            explain_for_error="Check your math",
            spec=CheckSpec(
                perform=PerformConfig(action="call_function", target="add", params={"args": [2, 3]}),
                expect=Expectation(
                    return_value=ExpectConfig(assertion="equals", value=5)
                )
            )
        )
        
        # Mock the action execution with unexpected exception
        with patch.object(self.check_handler, '_execute_action') as mock_execute:
            mock_execute.return_value = ActionResult(exception=RuntimeError("Unexpected error"))
            
            result = self.check_handler.execute_check(check_config, self.environment, self.context)
            
            self.assertFalse(result.passed)
            self.assertEqual(result.check_id, 4)
            self.assertIn("Action failed with exception", result.error_message)

    def test_execute_action_with_save_as(self):
        perform_config = PerformConfig(
            action="call_function",
            target="add",
            params={"args": [2, 3]},
            save_as="result"
        )
        
        # Mock the action factories dictionary
        mock_action_class = Mock()
        mock_action = Mock()
        mock_action.execute.return_value = ActionResult(return_value=5)
        mock_action_class.return_value = mock_action
        
        self.check_handler._action_factories["call_function"] = mock_action_class
        
        result = self.check_handler._execute_action(perform_config, self.environment, self.context)
        
        self.assertEqual(result.return_value, 5)
        self.assertTrue(self.context.has_object("result"))
        self.assertEqual(self.context.get_object("result"), 5)

    def test_check_expectations_return_value(self):
        expectation = Expectation(
            return_value=ExpectConfig(assertion="equals", value=5)
        )
        action_result = ActionResult(return_value=5)
        
        result = self.check_handler._check_expectations(expectation, action_result)
        
        self.assertTrue(result)

    def test_check_expectations_stdout(self):
        expectation = Expectation(
            stdout=ExpectConfig(assertion="contains", value="Hello")
        )
        action_result = ActionResult(stdout="Hello, World!")
        
        result = self.check_handler._check_expectations(expectation, action_result)
        
        self.assertTrue(result)

    def test_check_expectations_stderr(self):
        expectation = Expectation(
            stderr=ExpectConfig(assertion="equals", value="")
        )
        action_result = ActionResult(stderr="")
        
        result = self.check_handler._check_expectations(expectation, action_result)
        
        self.assertTrue(result)

    def test_format_error_message_with_placeholders(self):
        template = "Expected {expected}, got {actual}"
        action_result = ActionResult(return_value=5)
        expectation = Expectation(
            return_value=ExpectConfig(assertion="equals", value=10)
        )
        
        message = self.check_handler._format_error_message(template, action_result, expectation)
        
        self.assertEqual(message, "Expected 10, got 5")

    def test_format_error_message_without_placeholders(self):
        template = "Check failed"
        action_result = ActionResult(return_value=5)
        expectation = Expectation(
            return_value=ExpectConfig(assertion="equals", value=10)
        )
        
        message = self.check_handler._format_error_message(template, action_result, expectation)
        
        self.assertEqual(message, "Check failed")


if __name__ == '__main__':
    unittest.main()