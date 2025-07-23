from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from .container import DependencyContainer
from ..utils.exceptions import PluginError


@dataclass
class ComponentMetadata:
    name: str
    version: str
    test_types: List[str]
    dependencies: List[str] = field(default_factory=list)


class ComponentProvider(ABC):
    @property
    @abstractmethod
    def metadata(self) -> ComponentMetadata:
        pass
    
    @abstractmethod
    def register_components(self, container: DependencyContainer) -> None:
        pass


@dataclass
class PluginDescriptor:
    name: str
    provider: ComponentProvider
    metadata: ComponentMetadata
    is_loaded: bool = False


class PluginManager:
    def __init__(self, container: DependencyContainer):
        self._container = container
        self._plugins: Dict[str, PluginDescriptor] = {}
        self._loaded_order: List[str] = []
    
    def register_plugin(self, provider: ComponentProvider) -> None:
        metadata = provider.metadata
        
        if metadata.name in self._plugins:
            raise PluginError(f"Plugin '{metadata.name}' is already registered")
        
        descriptor = PluginDescriptor(
            name=metadata.name,
            provider=provider,
            metadata=metadata
        )
        
        self._plugins[metadata.name] = descriptor
    
    def load_plugin(self, plugin_name: str) -> None:
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin '{plugin_name}' is not registered")
        
        descriptor = self._plugins[plugin_name]
        
        if descriptor.is_loaded:
            return
        
        self._load_dependencies(descriptor)
        
        descriptor.provider.register_components(self._container)
        descriptor.is_loaded = True
        self._loaded_order.append(plugin_name)
    
    def load_all_plugins(self) -> None:
        for plugin_name in self._plugins:
            self.load_plugin(plugin_name)
    
    def get_providers_for_test_type(self, test_type: str) -> List[ComponentProvider]:
        providers = []
        for descriptor in self._plugins.values():
            if descriptor.is_loaded and test_type in descriptor.metadata.test_types:
                providers.append(descriptor.provider)
        return providers
    
    def _load_dependencies(self, descriptor: PluginDescriptor) -> None:
        for dep_name in descriptor.metadata.dependencies:
            if dep_name not in self._plugins:
                raise PluginError(f"Plugin '{descriptor.name}' depends on '{dep_name}' which is not registered")
            
            self.load_plugin(dep_name)


class PluginRegistry:
    _instance: Optional['PluginRegistry'] = None
    
    def __new__(cls) -> 'PluginRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers: List[ComponentProvider] = []
        return cls._instance
    
    def register(self, provider: ComponentProvider) -> None:
        self._providers.append(provider)
    
    def get_all_providers(self) -> List[ComponentProvider]:
        return self._providers.copy()
    
    def clear(self) -> None:
        self._providers.clear()


def plugin_provider(metadata: ComponentMetadata) -> Callable[[Type[ComponentProvider]], Type[ComponentProvider]]:
    def decorator(cls: Type[ComponentProvider]) -> Type[ComponentProvider]:
        class WrappedProvider(cls):
            @property
            def metadata(self) -> ComponentMetadata:
                return metadata
        
        registry = PluginRegistry()
        registry.register(WrappedProvider())
        
        return cls
    
    return decorator