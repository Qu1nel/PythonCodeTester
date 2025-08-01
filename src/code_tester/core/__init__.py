"""
Ядро фреймворка code-tester.

Этот пакет содержит основные компоненты новой архитектуры:
- DependencyContainer: IoC контейнер для управления зависимостями
- PluginManager: система управления плагинами
- ValidationService: валидация конфигураций
- TestSession: изолированное выполнение тестов
"""

from .container import (
    DependencyContainer,
    ScopedContainer,
    ServiceLifetime,
    ServiceDescriptor,
    IDisposable,
)
from .plugins import (
    ComponentMetadata,
    ComponentProvider,
    PluginManager,
    PluginRegistry,
    plugin_provider,
)

__all__ = [
    "DependencyContainer",
    "ScopedContainer", 
    "ServiceLifetime",
    "ServiceDescriptor",
    "IDisposable",
    "ComponentMetadata",
    "ComponentProvider",
    "PluginManager",
    "PluginRegistry",
    "plugin_provider",
]