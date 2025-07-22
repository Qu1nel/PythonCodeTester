from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .actions import PerformConfig
from .assertions import ExpectConfig
from .mocks import MockConfig


class Expectation(BaseModel):
    return_value: Optional[ExpectConfig] = Field(None, description="Expected return value")
    stdout: Optional[ExpectConfig] = Field(None, description="Expected stdout output")
    stderr: Optional[ExpectConfig] = Field(None, description="Expected stderr output")
    image: Optional[ExpectConfig] = Field(None, description="Expected image output (for arcade)")
    http_response: Optional[ExpectConfig] = Field(None, description="Expected HTTP response (for flask)")
    mock_calls: Optional[List[ExpectConfig]] = Field(None, description="Expected mock calls (for api)")
    
    @field_validator('mock_calls')
    @classmethod
    def validate_mock_calls(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("Mock calls list cannot be empty if provided")
        return v
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class CheckSpec(BaseModel):
    perform: PerformConfig = Field(..., description="Action to perform")
    expect: Expectation = Field(..., description="Expected results")
    mocks: List[MockConfig] = Field(default_factory=list, description="Mock configurations")
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class CheckConfig(BaseModel):
    check_id: int = Field(..., description="Unique ID for this check")
    name_for_output: str = Field(..., description="Human-readable name for output")
    reason_for_output: str = Field(..., description="Error message template with placeholders")
    explain_for_error: str = Field(..., description="Detailed explanation for students")
    spec: CheckSpec = Field(..., description="Check specification")
    is_critical: bool = Field(False, description="Whether failure should stop execution")
    
    @field_validator('check_id')
    @classmethod
    def validate_check_id(cls, v):
        if v <= 0:
            raise ValueError("Check ID must be positive")
        return v
    
    @field_validator('name_for_output', 'reason_for_output', 'explain_for_error')
    @classmethod
    def validate_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("String fields cannot be empty")
        return v.strip()
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class SetupActionConfig(BaseModel):
    action: str = Field(..., description="Action to perform during setup")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for the setup action")
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        if not v or not v.strip():
            raise ValueError("Action name cannot be empty")
        return v.strip()
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class TestCaseConfig(BaseModel):
    test_id: int = Field(..., description="Unique test case ID")
    test_name: str = Field(..., description="Human-readable test name")
    description: str = Field(..., description="Test description")
    test_type: str = Field(..., description="Type of test (py_general, api, flask, arcade)")
    checks: List[CheckConfig] = Field(..., description="List of checks to perform")
    setup_actions: List[SetupActionConfig] = Field(default_factory=list, description="Setup actions")
    teardown_actions: List[SetupActionConfig] = Field(default_factory=list, description="Teardown actions")
    
    @field_validator('test_id')
    @classmethod
    def validate_test_id(cls, v):
        if v <= 0:
            raise ValueError("Test ID must be positive")
        return v
    
    @field_validator('test_name', 'description')
    @classmethod
    def validate_strings(cls, v):
        if not v or not v.strip():
            raise ValueError("String fields cannot be empty")
        return v.strip()
    
    @field_validator('test_type')
    @classmethod
    def validate_test_type(cls, v):
        valid_types = {'py_general', 'api', 'flask', 'arcade'}
        if v not in valid_types:
            raise ValueError(f"Test type must be one of: {valid_types}")
        return v
    
    @field_validator('checks')
    @classmethod
    def validate_checks(cls, v):
        if not v:
            raise ValueError("At least one check is required")
        
        # Check for duplicate check IDs
        check_ids = [check.check_id for check in v]
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("Check IDs must be unique")
        
        return v
    
    model_config = ConfigDict(
        validate_assignment=True
    )