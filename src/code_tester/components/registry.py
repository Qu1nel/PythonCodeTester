from typing import Callable, Generic, Type, TypeVar

from ..exceptions import ConfigError

T = TypeVar("T")
K = TypeVar("K")


class Registry(Generic[K, T]):
    def __init__(self):
        self._registry: dict[K, Type[T]] = {}

    @property
    def get_all_registry(self) -> dict[K, Type[T]]:
        return self._registry

    def register(self, key: K) -> Callable[[Type[T]], Type[T]]:
        def decorator(cls: Type[T]) -> Type[T]:
            if key in self._registry:
                raise ConfigError(f"Duplicate component key registered: {key}")
            self._registry[key] = cls
            return cls

        return decorator

    def get(self, key: K) -> Type[T] | None:
        return self._registry.get(key)
