# Legacy import for backward compatibility
# New code should import from src.code_tester.utils directly

from .utils import create_dataclass_from_dict, create_pydantic_from_dict

__all__ = ["create_dataclass_from_dict", "create_pydantic_from_dict"]