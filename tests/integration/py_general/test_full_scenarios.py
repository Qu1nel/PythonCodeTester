import json
import pytest
from pathlib import Path

from code_tester.config import AppConfig
from code_tester.execution.tester import DynamicTester
from code_tester.logging import Console, LogLevel


class TestFullScenariosIntegration:
    
    @pytest.fixture
    def console(self):
        from code_tester.logging import LogConfig, setup_logger
        log_config = LogConfig(level=LogLevel.ERROR, console_enabled=False)
        logger = setup_logger(log_config)
        return Console(logger, is_quiet=True)
    
    def test_complex_multi_step_scenario(self, console):
        """Test a complex scenario with object creation, method calls, and context sharing."""
        
        complex_test_case = {
            "test_id": 100,
            "test_name": "Complex Multi-Step Test",
            "description": "Tests object creation, method calls, and context sharing",
            "test_type": "py_general",
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Create Calculator",
                    "reason_for_output": "Calculator creation failed",
                    "explain_for_error": "Calculator should be created successfully",
                    "spec": {
                        "perform": {
                            "action": "create_object",
                            "target": "Calculator",
                            "save_as": "my_calc"
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "is_instance_of",
                                "value": "Calculator"
                            }
                        }
                    }
                },
                {
                    "check_id": 2,
                    "name_for_output": "Perform Addition",
                    "reason_for_output": "Addition returned {actual}, expected {expected}",
                    "explain_for_error": "Addition should work correctly",
                    "spec": {
                        "perform": {
                            "action": "call_method",
                            "target": "add",
                            "params": {
                                "object_ref": "my_calc",
                                "args": [10, 5]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": 15
                            }
                        }
                    }
                },
                {
                    "check_id": 3,
                    "name_for_output": "Perform Multiplication",
                    "reason_for_output": "Multiplication returned {actual}, expected {expected}",
                    "explain_for_error": "Multiplication should work correctly",
                    "spec": {
                        "perform": {
                            "action": "call_method",
                            "target": "multiply",
                            "params": {
                                "object_ref": "my_calc",
                                "args": [4, 7]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": 28
                            }
                        }
                    }
                },
                {
                    "check_id": 4,
                    "name_for_output": "Check History Length",
                    "reason_for_output": "History should contain {expected} entries, got {actual}",
                    "explain_for_error": "History should track all operations",
                    "spec": {
                        "perform": {
                            "action": "call_method",
                            "target": "get_history",
                            "params": {
                                "object_ref": "my_calc"
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "has_length",
                                "value": 2
                            }
                        }
                    }
                },
                {
                    "check_id": 5,
                    "name_for_output": "Test Function Call",
                    "reason_for_output": "Area calculation returned {actual}, expected {expected}",
                    "explain_for_error": "Area calculation should work correctly",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "calculate_area",
                            "params": {
                                "args": [6, 8]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": 48
                            }
                        }
                    }
                }
            ]
        }
        
        # Create temporary test case file
        test_case_path = Path("tests/fixtures/test_cases/py_general/complex_test.json")
        test_case_path.write_text(json.dumps(complex_test_case, indent=2))
        
        try:
            config = AppConfig(
                solution_path=Path("tests/fixtures/solutions/py_general/calculator.py"),
                test_case_path=test_case_path,
                max_messages=10,
                exit_on_first_error=False
            )
            
            tester = DynamicTester(config, console)
            result = tester.run()
            
            assert result is True, "Complex scenario should pass"
            assert len(tester.failed_checks_ids) == 0, f"No checks should fail, but failed: {tester.failed_checks_ids}"
            
        finally:
            if test_case_path.exists():
                test_case_path.unlink()
    
    def test_error_handling_scenario(self, console):
        """Test error handling in various scenarios."""
        
        error_test_case = {
            "test_id": 101,
            "test_name": "Error Handling Test",
            "description": "Tests proper error handling",
            "test_type": "py_general",
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Test Division by Zero",
                    "reason_for_output": "Should raise ValueError for division by zero",
                    "explain_for_error": "Division by zero should raise ValueError",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "calculate_area",
                            "params": {
                                "args": [-5, 3]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "raises_exception",
                                "value": "ValueError"
                            }
                        }
                    }
                },
                {
                    "check_id": 2,
                    "name_for_output": "Test Fibonacci Edge Case",
                    "reason_for_output": "fibonacci(0) should return {expected}, got {actual}",
                    "explain_for_error": "Fibonacci of 0 should be 0",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "fibonacci",
                            "params": {
                                "args": [0]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": 0
                            }
                        }
                    }
                }
            ]
        }
        
        # Create temporary test case file
        test_case_path = Path("tests/fixtures/test_cases/py_general/error_test.json")
        test_case_path.write_text(json.dumps(error_test_case, indent=2))
        
        try:
            config = AppConfig(
                solution_path=Path("tests/fixtures/solutions/py_general/calculator.py"),
                test_case_path=test_case_path,
                max_messages=10,
                exit_on_first_error=False
            )
            
            tester = DynamicTester(config, console)
            result = tester.run()
            
            assert result is True, "Error handling scenario should pass"
            assert len(tester.failed_checks_ids) == 0, f"No checks should fail, but failed: {tester.failed_checks_ids}"
            
        finally:
            if test_case_path.exists():
                test_case_path.unlink()
    
    def test_context_sharing_between_checks(self, console):
        """Test that context is properly shared between checks."""
        
        context_test_case = {
            "test_id": 102,
            "test_name": "Context Sharing Test",
            "description": "Tests context sharing between checks",
            "test_type": "py_general",
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Create and Save Calculator",
                    "reason_for_output": "Calculator creation failed",
                    "explain_for_error": "Calculator should be created and saved",
                    "spec": {
                        "perform": {
                            "action": "create_object",
                            "target": "Calculator",
                            "save_as": "shared_calc"
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "is_instance_of",
                                "value": "Calculator"
                            }
                        }
                    }
                },
                {
                    "check_id": 2,
                    "name_for_output": "Use Saved Calculator",
                    "reason_for_output": "Using saved calculator failed",
                    "explain_for_error": "Should be able to use saved calculator",
                    "spec": {
                        "perform": {
                            "action": "call_method",
                            "target": "add",
                            "params": {
                                "object_ref": "shared_calc",
                                "args": [20, 30]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": 50
                            }
                        }
                    }
                },
                {
                    "check_id": 3,
                    "name_for_output": "Verify History Persistence",
                    "reason_for_output": "History should persist across method calls",
                    "explain_for_error": "History should contain the previous operation",
                    "spec": {
                        "perform": {
                            "action": "call_method",
                            "target": "get_history",
                            "params": {
                                "object_ref": "shared_calc"
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "contains",
                                "value": "20 + 30 = 50"
                            }
                        }
                    }
                }
            ]
        }
        
        # Create temporary test case file
        test_case_path = Path("tests/fixtures/test_cases/py_general/context_test.json")
        test_case_path.write_text(json.dumps(context_test_case, indent=2))
        
        try:
            config = AppConfig(
                solution_path=Path("tests/fixtures/solutions/py_general/calculator.py"),
                test_case_path=test_case_path,
                max_messages=10,
                exit_on_first_error=False
            )
            
            tester = DynamicTester(config, console)
            result = tester.run()
            
            assert result is True, "Context sharing scenario should pass"
            assert len(tester.failed_checks_ids) == 0, f"No checks should fail, but failed: {tester.failed_checks_ids}"
            
        finally:
            if test_case_path.exists():
                test_case_path.unlink()