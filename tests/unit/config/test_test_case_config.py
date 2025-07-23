import pytest
from pydantic import ValidationError

from code_tester.config import TestCaseConfig, CheckConfig, CheckSpec, Expectation, PerformConfig, ExpectConfig


class TestTestCaseConfig:
    def test_valid_test_case_creation(self):
        perform = PerformConfig(action="run_script")
        expect = ExpectConfig(assertion="equals", value="Hello")
        expectation = Expectation(stdout=expect)
        spec = CheckSpec(perform=perform, expect=expectation)
        check = CheckConfig(
            check_id=1,
            name_for_output="Test output",
            reason_for_output="Expected {expected}, got {actual}",
            explain_for_error="Check your code",
            spec=spec
        )
        
        config = TestCaseConfig(
            test_id=1,
            test_name="Sample Test",
            description="A sample test",
            test_type="py_general",
            checks=[check]
        )
        
        assert config.test_id == 1
        assert config.test_name == "Sample Test"
        assert config.test_type == "py_general"
        assert len(config.checks) == 1
        assert len(config.setup_actions) == 0

    def test_invalid_test_type_raises_error(self):
        perform = PerformConfig(action="run_script")
        expect = ExpectConfig(assertion="equals", value="Hello")
        expectation = Expectation(stdout=expect)
        spec = CheckSpec(perform=perform, expect=expectation)
        check = CheckConfig(
            check_id=1,
            name_for_output="Test output",
            reason_for_output="Expected {expected}, got {actual}",
            explain_for_error="Check your code",
            spec=spec
        )
        
        with pytest.raises(ValidationError) as exc_info:
            TestCaseConfig(
                test_id=1,
                test_name="Sample Test",
                description="A sample test",
                test_type="invalid_type",
                checks=[check]
            )
        
        assert "Test type must be one of" in str(exc_info.value)

    def test_duplicate_check_ids_raises_error(self):
        perform = PerformConfig(action="run_script")
        expect = ExpectConfig(assertion="equals", value="Hello")
        expectation = Expectation(stdout=expect)
        spec = CheckSpec(perform=perform, expect=expectation)
        
        check1 = CheckConfig(
            check_id=1,
            name_for_output="Test 1",
            reason_for_output="Error 1",
            explain_for_error="Explain 1",
            spec=spec
        )
        check2 = CheckConfig(
            check_id=1,  # Duplicate ID
            name_for_output="Test 2",
            reason_for_output="Error 2",
            explain_for_error="Explain 2",
            spec=spec
        )
        
        with pytest.raises(ValidationError) as exc_info:
            TestCaseConfig(
                test_id=1,
                test_name="Sample Test",
                description="A sample test",
                test_type="py_general",
                checks=[check1, check2]
            )
        
        assert "Check IDs must be unique" in str(exc_info.value)

    def test_empty_checks_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            TestCaseConfig(
                test_id=1,
                test_name="Sample Test",
                description="A sample test",
                test_type="py_general",
                checks=[]
            )
        
        assert "At least one check is required" in str(exc_info.value)