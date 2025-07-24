import json
import pytest
from pathlib import Path

from code_tester.config import AppConfig
from code_tester.execution.tester import DynamicTester
from code_tester.logging import Console, LogLevel


class TestCalculatorIntegration:
    
    @pytest.fixture
    def calculator_solution_path(self):
        return Path("tests/fixtures/solutions/py_general/calculator.py")
    
    @pytest.fixture
    def calculator_test_case_path(self):
        return Path("tests/fixtures/test_cases/py_general/calculator_test.json")
    
    @pytest.fixture
    def console(self):
        from code_tester.logging import LogConfig, setup_logger
        log_config = LogConfig(level=LogLevel.ERROR, console_enabled=False)
        logger = setup_logger(log_config)
        return Console(logger, is_quiet=True)
    
    def test_calculator_full_scenario(self, calculator_solution_path, calculator_test_case_path, console):
        config = AppConfig(
            solution_path=calculator_solution_path,
            test_case_path=calculator_test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        assert result is True, "Calculator test should pass completely"
        assert len(tester.failed_checks_ids) == 0, f"No checks should fail, but failed: {tester.failed_checks_ids}"
    
    def test_calculator_object_creation_and_methods(self, calculator_solution_path, calculator_test_case_path, console):
        config = AppConfig(
            solution_path=calculator_solution_path,
            test_case_path=calculator_test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        tester._load_and_parse_test_case()
        tester._setup_environment()
        
        test_case = tester.test_case_config
        assert test_case is not None
        assert test_case.test_name == "Calculator Class Test"
        assert len(test_case.checks) == 3
        
        check_names = [check.name_for_output for check in test_case.checks]
        expected_names = [
            "Test Calculator creation",
            "Test addition method", 
            "Test division by zero"
        ]
        assert check_names == expected_names
    
    def test_calculator_with_exit_on_first_error(self, calculator_solution_path, console):
        bad_test_case = {
            "test_id": 1,
            "test_name": "Bad Calculator Test",
            "description": "Test with intentional failure",
            "test_type": "py_general",
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Test bad addition",
                    "reason_for_output": "Addition should return {expected}, got {actual}",
                    "explain_for_error": "This should fail",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "calculate_area",
                            "params": {
                                "args": [5, 3]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": 999
                            }
                        }
                    }
                },
                {
                    "check_id": 2,
                    "name_for_output": "This should not run",
                    "reason_for_output": "Should not reach here",
                    "explain_for_error": "Should not reach here",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "calculate_area",
                            "params": {
                                "args": [2, 2]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": 4
                            }
                        }
                    }
                }
            ]
        }
        
        test_case_path = Path("tests/fixtures/test_cases/py_general/bad_test.json")
        test_case_path.write_text(json.dumps(bad_test_case, indent=2))
        
        try:
            config = AppConfig(
                solution_path=calculator_solution_path,
                test_case_path=test_case_path,
                max_messages=10,
                exit_on_first_error=True
            )
            
            tester = DynamicTester(config, console)
            result = tester.run()
            
            assert result is False, "Test should fail"
            assert len(tester.failed_checks_ids) == 1, "Should stop after first failure"
            assert tester.failed_checks_ids[0] == 1, "First check should fail"
        finally:
            if test_case_path.exists():
                test_case_path.unlink()