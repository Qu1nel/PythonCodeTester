import pytest
from pathlib import Path

from code_tester.config import AppConfig
from code_tester.execution.tester import DynamicTester
from code_tester.logging import Console, LogLevel


class TestFunctionsIntegration:
    
    @pytest.fixture
    def functions_solution_path(self):
        return Path("tests/fixtures/solutions/py_general/simple_functions.py")
    
    @pytest.fixture
    def functions_test_case_path(self):
        return Path("tests/fixtures/test_cases/py_general/function_tests.json")
    
    @pytest.fixture
    def console(self):
        from code_tester.logging import LogConfig, setup_logger
        log_config = LogConfig(level=LogLevel.ERROR, console_enabled=False)
        logger = setup_logger(log_config)
        return Console(logger, is_quiet=True)
    
    def test_mathematical_functions_full_scenario(self, functions_solution_path, functions_test_case_path, console):
        config = AppConfig(
            solution_path=functions_solution_path,
            test_case_path=functions_test_case_path,
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        result = tester.run()
        
        assert result is True, "Mathematical functions test should pass completely"
        assert len(tester.failed_checks_ids) == 0, f"No checks should fail, but failed: {tester.failed_checks_ids}"
    
    def test_individual_function_calls(self, functions_solution_path, console):
        config = AppConfig(
            solution_path=functions_solution_path,
            test_case_path=Path("dummy.json"),
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        tester._setup_environment()
        
        # Test direct function calls through environment
        env = tester._environment
        
        with env.run_in_isolation() as (module, captured_output):
            # Test factorial
            factorial_func = getattr(module, 'factorial')
            assert factorial_func(5) == 120
            assert factorial_func(0) == 1
            
            # Test fibonacci
            fibonacci_func = getattr(module, 'fibonacci')
            assert fibonacci_func(7) == 13
            assert fibonacci_func(6) == 8
            
            # Test is_prime
            is_prime_func = getattr(module, 'is_prime')
            assert is_prime_func(17) is True
            assert is_prime_func(16) is False
            assert is_prime_func(2) is True
    
    def test_function_error_handling(self, functions_solution_path, console):
        config = AppConfig(
            solution_path=functions_solution_path,
            test_case_path=Path("dummy.json"),
            max_messages=10,
            exit_on_first_error=False
        )
        
        tester = DynamicTester(config, console)
        tester._setup_environment()
        
        env = tester._environment
        
        with env.run_in_isolation() as (module, captured_output):
            # Test factorial with negative number
            factorial_func = getattr(module, 'factorial')
            with pytest.raises(ValueError, match="Factorial is not defined for negative numbers"):
                factorial_func(-1)
            
            # Test fibonacci with negative number
            fibonacci_func = getattr(module, 'fibonacci')
            with pytest.raises(ValueError, match="n must be non-negative"):
                fibonacci_func(-1)
            
            # Test divide by zero
            divide_func = getattr(module, 'divide')
            with pytest.raises(ValueError, match="Cannot divide by zero"):
                divide_func(10, 0)