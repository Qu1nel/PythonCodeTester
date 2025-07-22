from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class MockConfig(BaseModel):
    target_path: str = Field(..., description="Full path to the object to mock (e.g., 'requests.get')")
    behavior: Dict[str, Any] = Field(..., description="Mock behavior configuration")
    save_as: Optional[str] = Field(None, description="Name to save the mock under for later reference")
    
    @field_validator('target_path')
    @classmethod
    def validate_target_path(cls, v):
        if not v or not v.strip():
            raise ValueError("Target path cannot be empty")
        if '.' not in v:
            raise ValueError("Target path must contain at least one dot (module.object)")
        return v.strip()
    
    @field_validator('behavior')
    @classmethod
    def validate_behavior(cls, v):
        if not v:
            raise ValueError("Behavior configuration cannot be empty")
        
        valid_keys = {'return_value', 'return_object', 'side_effect'}
        if not any(key in v for key in valid_keys):
            raise ValueError(f"Behavior must contain at least one of: {valid_keys}")
        
        return v
    
    @field_validator('save_as')
    @classmethod
    def validate_save_as(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Save as name cannot be empty string")
        return v.strip() if v else v
    
    model_config = ConfigDict(
        validate_assignment=True
    )