"""Helper functions for data conversion and utilities."""

from typing import Any, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def create_pydantic_from_dict(cls: Type[T], data: dict[str, Any]) -> T:
    """Create a Pydantic model instance from a dictionary.
    
    Args:
        cls: The Pydantic model class to create
        data: Dictionary with data to populate the model
        
    Returns:
        Instance of the Pydantic model
        
    Raises:
        TypeError: If cls is not a Pydantic BaseModel subclass
    """
    if not issubclass(cls, BaseModel):
        raise TypeError(f"Target class {cls.__name__} is not a pydantic BaseModel.")
    
    return cls.model_validate(data)


def create_dataclass_from_dict(cls: Type[T], data: dict[str, Any]) -> T:
    """Legacy function for backward compatibility.
    
    Args:
        cls: The Pydantic model class to create
        data: Dictionary with data to populate the model
        
    Returns:
        Instance of the Pydantic model
    """
    return create_pydantic_from_dict(cls, data)