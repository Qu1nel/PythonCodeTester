from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict


class PerformConfig(BaseModel):
    action: str = Field(..., description="Name of the action to perform")
    target: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Target for the action")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameters for the action")
    save_as: Optional[str] = Field(None, description="Name to save the result under")
    start_from_object_ref: Optional[str] = Field(None, description="Object reference to start from (for arcade)")
    
    @field_validator('action')
    @classmethod
    def validate_action_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Action name cannot be empty")
        return v.strip()
    
    @field_validator('save_as', 'start_from_object_ref')
    @classmethod
    def validate_identifiers(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Identifier cannot be empty string")
        return v.strip() if v else v
    
    model_config = ConfigDict(
        validate_assignment=True
    )