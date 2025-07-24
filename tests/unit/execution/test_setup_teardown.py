import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from code_tester.config import AppConfig
from code_tester.execution.tester import DynamicTester
from code_tester.logging import Console, LogConfig, LogLevel, setup_logger


class TestSetupTeardownActions:
    
    @pytest.fixture
    def console(self):
        log_config = LogConfig(level=LogLevel.ERROR, console_enabled=False)
        logger = setup_logger(log_config)
        return Console(logger, is_quiet=True)
    
    @pytest.fixture
    def simple_solution_path(self, tmp_path):
        solution_file = tmp_path / "solution.py"
        solution_file.write_text(f"""
import os
from pathlib import Path

# Use the test's temporary directory
TEST_DIR = Path(r"{tmp_path}")

def create_file(filename, content):
    file_path = TEST_DIR / filename
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Created {{filename}}"

def read_file(filename):
    file_path = TEST_DIR / filename
    with open(file_path, 'r') as f:
        return f.read()

def delete_file(filename):
    file_path = TEST_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return f"Deleted {{filename}}"
    return f"File {{filename}} not found"
""")
        return solution_file
    
    def test_setup_actions_success(self, simple_solution_path, console, tmp_path):
        test_case = {
            "test_id": 1,
            "test_name": "Setup Test",
            "description": "Test with setup actions",
            "test_type": "py_general",
            "setup_actions": [
                {
                    "action": "call_function",
                    "target": "create_file",
                    "params": {
                        "args": ["test_file.txt", "Hello World"]
                    }
                }
            ],
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Test file reading",
                    "reason_for_output": "Should read file content",
                    "explain_for_error": "File should exist after setup",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "read_file",
                            "params": {
                                "args": ["test_file.txt"]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": "Hello World"
                            }
                        }
                    }
                }
            ]
        }
        
        test_case_path = tmp_path / "test_case.json"
        test_case_path.write_text(json.dumps(test_case, indent=2))
        
        config = AppConfig(
            solution_path=simple_solution_path,
            test_case_path=test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        print(f"Test result: {result}")
        print(f"Failed checks: {tester.failed_checks_ids}")
        if tester._failed_checks:
            for check in tester._failed_checks:
                print(f"Failed check {check.check_id}: {check.error_message}")
                if check.exception:
                    print(f"Exception: {check.exception}")
        else:
            print("No failed checks - issue might be in setup/teardown execution")
        
        assert result is True, "Test should pass with setup actions"
        assert len(tester.failed_checks_ids) == 0
    
    def test_setup_actions_failure_aborts_test(self, simple_solution_path, console, tmp_path):
        test_case = {
            "test_id": 1,
            "test_name": "Setup Failure Test",
            "description": "Test with failing setup actions",
            "test_type": "py_general",
            "setup_actions": [
                {
                    "action": "call_function",
                    "target": "nonexistent_function",
                    "params": {
                        "args": []
                    }
                }
            ],
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "This should not run",
                    "reason_for_output": "Should not reach here",
                    "explain_for_error": "Should not reach here",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "read_file",
                            "params": {
                                "args": ["test_file.txt"]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": "Hello World"
                            }
                        }
                    }
                }
            ]
        }
        
        test_case_path = tmp_path / "test_case.json"
        test_case_path.write_text(json.dumps(test_case, indent=2))
        
        config = AppConfig(
            solution_path=simple_solution_path,
            test_case_path=test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        assert result is False, "Test should fail due to setup failure"
        assert len(tester.failed_checks_ids) == 0, "No checks should have run"
    
    def test_teardown_actions_success(self, simple_solution_path, console, tmp_path):
        test_case = {
            "test_id": 1,
            "test_name": "Teardown Test",
            "description": "Test with teardown actions",
            "test_type": "py_general",
            "setup_actions": [
                {
                    "action": "call_function",
                    "target": "create_file",
                    "params": {
                        "args": ["temp_file.txt", "Temporary content"]
                    }
                }
            ],
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Test file exists",
                    "reason_for_output": "File should exist",
                    "explain_for_error": "File should be created by setup",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "read_file",
                            "params": {
                                "args": ["temp_file.txt"]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": "Temporary content"
                            }
                        }
                    }
                }
            ],
            "teardown_actions": [
                {
                    "action": "call_function",
                    "target": "delete_file",
                    "params": {
                        "args": ["temp_file.txt"]
                    }
                }
            ]
        }
        
        test_case_path = tmp_path / "test_case.json"
        test_case_path.write_text(json.dumps(test_case, indent=2))
        
        config = AppConfig(
            solution_path=simple_solution_path,
            test_case_path=test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        assert result is True, "Test should pass with teardown actions"
        assert len(tester.failed_checks_ids) == 0
        
        # Verify file was cleaned up
        assert not (tmp_path / "temp_file.txt").exists(), "File should be deleted by teardown"
    
    def test_teardown_actions_run_even_on_test_failure(self, simple_solution_path, console, tmp_path):
        test_case = {
            "test_id": 1,
            "test_name": "Teardown on Failure Test",
            "description": "Test that teardown runs even when tests fail",
            "test_type": "py_general",
            "setup_actions": [
                {
                    "action": "call_function",
                    "target": "create_file",
                    "params": {
                        "args": ["cleanup_test.txt", "Should be cleaned up"]
                    }
                }
            ],
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Failing test",
                    "reason_for_output": "This test will fail",
                    "explain_for_error": "Intentional failure",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "read_file",
                            "params": {
                                "args": ["cleanup_test.txt"]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": "Wrong content"
                            }
                        }
                    }
                }
            ],
            "teardown_actions": [
                {
                    "action": "call_function",
                    "target": "delete_file",
                    "params": {
                        "args": ["cleanup_test.txt"]
                    }
                }
            ]
        }
        
        test_case_path = tmp_path / "test_case.json"
        test_case_path.write_text(json.dumps(test_case, indent=2))
        
        config = AppConfig(
            solution_path=simple_solution_path,
            test_case_path=test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        assert result is False, "Test should fail"
        assert len(tester.failed_checks_ids) == 1, "One check should fail"
        
        # Verify file was still cleaned up despite test failure
        assert not (tmp_path / "cleanup_test.txt").exists(), "File should be deleted by teardown even on test failure"
    
    def test_teardown_failure_logs_warning_but_continues(self, simple_solution_path, console, tmp_path):
        test_case = {
            "test_id": 1,
            "test_name": "Teardown Failure Test",
            "description": "Test that teardown failures are logged as warnings",
            "test_type": "py_general",
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Simple test",
                    "reason_for_output": "Should pass",
                    "explain_for_error": "Simple test",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "create_file",
                            "params": {
                                "args": ["test.txt", "content"]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": "Created test.txt"
                            }
                        }
                    }
                }
            ],
            "teardown_actions": [
                {
                    "action": "call_function",
                    "target": "nonexistent_teardown_function",
                    "params": {
                        "args": []
                    }
                }
            ]
        }
        
        test_case_path = tmp_path / "test_case.json"
        test_case_path.write_text(json.dumps(test_case, indent=2))
        
        config = AppConfig(
            solution_path=simple_solution_path,
            test_case_path=test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        # Test should still pass despite teardown failure
        assert result is True, "Test should pass despite teardown failure"
        assert len(tester.failed_checks_ids) == 0, "Main test should pass"
    
    def test_no_setup_teardown_actions(self, simple_solution_path, console, tmp_path):
        test_case = {
            "test_id": 1,
            "test_name": "No Setup/Teardown Test",
            "description": "Test without setup or teardown actions",
            "test_type": "py_general",
            "checks": [
                {
                    "check_id": 1,
                    "name_for_output": "Simple test",
                    "reason_for_output": "Should pass",
                    "explain_for_error": "Simple test",
                    "spec": {
                        "perform": {
                            "action": "call_function",
                            "target": "create_file",
                            "params": {
                                "args": ["simple.txt", "simple content"]
                            }
                        },
                        "expect": {
                            "return_value": {
                                "assertion": "equals",
                                "value": "Created simple.txt"
                            }
                        }
                    }
                }
            ]
        }
        
        test_case_path = tmp_path / "test_case.json"
        test_case_path.write_text(json.dumps(test_case, indent=2))
        
        config = AppConfig(
            solution_path=simple_solution_path,
            test_case_path=test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        assert result is True, "Test should pass without setup/teardown"
        assert len(tester.failed_checks_ids) == 0