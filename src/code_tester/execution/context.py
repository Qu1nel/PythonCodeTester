from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class ExecutionContext:
    def __init__(self):
        self._objects: Dict[str, Any] = {}
        self._variables: Dict[str, Any] = {}
    
    def save_object(self, name: str, obj: Any) -> None:
        self._objects[name] = obj
    
    def get_object(self, name: str) -> Any:
        if name not in self._objects:
            raise KeyError(f"Object '{name}' not found in context")
        return self._objects[name]
    
    def has_object(self, name: str) -> bool:
        return name in self._objects
    
    def save_variable(self, name: str, value: Any) -> None:
        self._variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        if name not in self._variables:
            raise KeyError(f"Variable '{name}' not found in context")
        return self._variables[name]
    
    def has_variable(self, name: str) -> bool:
        return name in self._variables
    
    def clear(self) -> None:
        self._objects.clear()
        self._variables.clear()
    
    def get_all_objects(self) -> Dict[str, Any]:
        return self._objects.copy()
    
    def get_all_variables(self) -> Dict[str, Any]:
        return self._variables.copy()


class ObjectStore:
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._type_hints: Dict[str, str] = {}
    
    def store(self, key: str, value: Any, type_hint: Optional[str] = None) -> None:
        self._store[key] = value
        if type_hint:
            self._type_hints[key] = type_hint
    
    def retrieve(self, key: str) -> Any:
        if key not in self._store:
            raise KeyError(f"Key '{key}' not found in store")
        return self._store[key]
    
    def exists(self, key: str) -> bool:
        return key in self._store
    
    def get_type_hint(self, key: str) -> Optional[str]:
        return self._type_hints.get(key)
    
    def remove(self, key: str) -> None:
        if key in self._store:
            del self._store[key]
        if key in self._type_hints:
            del self._type_hints[key]
    
    def clear(self) -> None:
        self._store.clear()
        self._type_hints.clear()
    
    def keys(self) -> list[str]:
        return list(self._store.keys())
    
    def values(self) -> list[Any]:
        return list(self._store.values())
    
    def items(self) -> list[tuple[str, Any]]:
        return list(self._store.items())