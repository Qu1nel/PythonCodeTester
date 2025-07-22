from typing import Any, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def create_pydantic_from_dict(cls: Type[T], data: dict[str, Any]) -> T:
    if not issubclass(cls, BaseModel):
        raise TypeError(f"Target class {cls.__name__} is not a pydantic BaseModel.")
    
    return cls.model_validate(data)


def create_dataclass_from_dict(cls: Type[T], data: dict[str, Any]) -> T:
    return create_pydantic_from_dict(cls, data)
