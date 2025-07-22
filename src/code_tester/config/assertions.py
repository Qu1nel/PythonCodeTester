from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ExpectConfig(BaseModel):
    assertion: str = Field(..., description="Name of the assertion to use")
    value: Optional[Any] = Field(None, description="Expected value for the assertion")
    target_mock: Optional[str] = Field(None, description="Target mock for mock assertions")
    tolerance: Optional[float] = Field(None, description="Tolerance for numeric comparisons")
    
    @field_validator('assertion')
    @classmethod
    def validate_assertion_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Assertion name cannot be empty")
        return v.strip()
    
    @field_validator('tolerance')
    @classmethod
    def validate_tolerance(cls, v):
        if v is not None and v < 0:
            raise ValueError("Tolerance must be non-negative")
        return v
    
    @field_validator('target_mock')
    @classmethod
    def validate_target_mock(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Target mock name cannot be empty string")
        return v.strip() if v else v
    
    model_config = ConfigDict(
        validate_assignment=True
    )