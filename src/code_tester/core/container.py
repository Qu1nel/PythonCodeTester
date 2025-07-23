"""
Dependency Injection Container для управления зависимостями в code-tester.

Этот модуль реализует IoC (Inversion of Control) контейнер, который позволяет:
- Регистрировать сервисы как singleton, transient или scoped
- Автоматически разрешать зависимости через конструкторы
- Создавать изолированные scope'ы для тестовых сессий
- Управлять жизненным циклом объектов
"""

import inspect
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar, get_type_hints

from ..utils.exceptions import DependencyResolutionError, CircularDependencyError

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Время жизни сервиса в DI контейнере."""
    
    SINGLETON = "singleton"  # Один экземпляр на весь контейнер
    TRANSIENT = "transient"  # Новый экземпляр при каждом запросе
    SCOPED = "scoped"        # Один экземпляр на scope


class ServiceDescriptor:
    """Описание сервиса в DI контейнере."""
    
    def __init__(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        instance: Optional[T] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ):
        self.service_type = service_type
        self.implementation_type = implementation_type
        self.factory = factory
        self.instance = instance
        self.lifetime = lifetime
        
        # Валидация
        if sum(x is not None for x in [implementation_type, factory, instance]) != 1:
            raise ValueError("Exactly one of implementation_type, factory, or instance must be provided")


class DependencyContainer:
    """
    IoC контейнер для управления зависимостями.
    
    Поддерживает три типа регистрации сервисов:
    - Singleton: один экземпляр на весь контейнер
    - Transient: новый экземпляр при каждом запросе
    - Scoped: один экземпляр на scope (для изоляции тестов)
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._resolution_stack: list[Type] = []  # Для обнаружения циклических зависимостей
    
    def register_singleton(self, service_type: Type[T], implementation_type: Type[T]) -> None:
        """
        Регистрирует сервис как singleton.
        
        Args:
            service_type: Интерфейс или базовый класс
            implementation_type: Конкретная реализация
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
    
    def register_transient(self, service_type: Type[T], implementation_type: Type[T]) -> None:
        """
        Регистрирует сервис как transient.
        
        Args:
            service_type: Интерфейс или базовый класс
            implementation_type: Конкретная реализация
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            lifetime=ServiceLifetime.TRANSIENT
        )
        self._services[service_type] = descriptor
    
    def register_scoped(self, service_type: Type[T], implementation_type: Type[T]) -> None:
        """
        Регистрирует сервис как scoped.
        
        Args:
            service_type: Интерфейс или базовый класс
            implementation_type: Конкретная реализация
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            lifetime=ServiceLifetime.SCOPED
        )
        self._services[service_type] = descriptor
    
    def register_factory(self, service_type: Type[T], factory: Callable[..., T], lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> None:
        """
        Регистрирует фабрику для создания сервиса.
        
        Args:
            service_type: Тип сервиса
            factory: Фабричная функция
            lifetime: Время жизни сервиса
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifetime=lifetime
        )
        self._services[service_type] = descriptor
    
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """
        Регистрирует готовый экземпляр как singleton.
        
        Args:
            service_type: Тип сервиса
            instance: Готовый экземпляр
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            instance=instance,
            lifetime=ServiceLifetime.SINGLETON
        )
        self._services[service_type] = descriptor
        self._singletons[service_type] = instance
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Разрешает зависимость и возвращает экземпляр сервиса.
        
        Args:
            service_type: Тип запрашиваемого сервиса
            
        Returns:
            Экземпляр сервиса
            
        Raises:
            DependencyResolutionError: Если сервис не зарегистрирован или не может быть создан
            CircularDependencyError: Если обнаружена циклическая зависимость
        """
        # Проверка циклических зависимостей
        if service_type in self._resolution_stack:
            cycle = " -> ".join(cls.__name__ for cls in self._resolution_stack[self._resolution_stack.index(service_type):])
            raise CircularDependencyError(f"Circular dependency detected: {cycle} -> {service_type.__name__}")
        
        # Проверка регистрации
        if service_type not in self._services:
            raise DependencyResolutionError(f"Service {service_type.__name__} is not registered")
        
        descriptor = self._services[service_type]
        
        # Singleton - возвращаем существующий экземпляр или создаем новый
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]
            
            instance = self._create_instance(descriptor)
            self._singletons[service_type] = instance
            return instance
        
        # Transient - всегда создаем новый экземпляр
        elif descriptor.lifetime == ServiceLifetime.TRANSIENT:
            return self._create_instance(descriptor)
        
        # Scoped - обрабатывается в ScopedContainer
        else:
            raise DependencyResolutionError(f"Scoped services must be resolved through ScopedContainer")
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Создает экземпляр сервиса на основе дескриптора."""
        self._resolution_stack.append(descriptor.service_type)
        
        try:
            # Готовый экземпляр
            if descriptor.instance is not None:
                return descriptor.instance
            
            # Фабричная функция
            if descriptor.factory is not None:
                return self._call_with_dependency_injection(descriptor.factory)
            
            # Класс реализации
            if descriptor.implementation_type is not None:
                return self._create_instance_from_type(descriptor.implementation_type)
            
            raise DependencyResolutionError(f"Invalid service descriptor for {descriptor.service_type.__name__}")
        
        finally:
            self._resolution_stack.pop()
    
    def _create_instance_from_type(self, implementation_type: Type[T]) -> T:
        """Создает экземпляр класса с автоматическим разрешением зависимостей."""
        return self._call_with_dependency_injection(implementation_type)
    
    def _call_with_dependency_injection(self, callable_obj: Callable[..., T]) -> T:
        """
        Вызывает функцию или конструктор с автоматическим разрешением зависимостей.
        
        Анализирует сигнатуру функции и автоматически разрешает все параметры,
        которые зарегистрированы в контейнере.
        """
        # Получаем сигнатуру
        signature = inspect.signature(callable_obj)
        try:
            type_hints = get_type_hints(callable_obj)
        except (NameError, AttributeError):
            # Fallback для forward references - используем raw annotations
            type_hints = getattr(callable_obj, '__annotations__', {})
        
        # Разрешаем параметры
        kwargs = {}
        for param_name, param in signature.parameters.items():
            # Пропускаем self для методов
            if param_name == 'self':
                continue
            
            # Получаем тип параметра
            param_type = type_hints.get(param_name)
            if param_type is None:
                # Если тип не указан, пропускаем
                if param.default is not inspect.Parameter.empty:
                    continue
                raise DependencyResolutionError(
                    f"Cannot resolve parameter '{param_name}' in {callable_obj}: no type hint provided"
                )
            
            # Пытаемся разрешить зависимость
            if param_type in self._services:
                kwargs[param_name] = self.resolve(param_type)
            elif param.default is not inspect.Parameter.empty:
                # Используем значение по умолчанию
                continue
            else:
                raise DependencyResolutionError(
                    f"Cannot resolve parameter '{param_name}' of type {param_type.__name__} in {callable_obj}"
                )
        
        return callable_obj(**kwargs)
    
    def create_scope(self) -> 'ScopedContainer':
        """
        Создает scoped контейнер для изоляции сервисов.
        
        Returns:
            Новый ScopedContainer
        """
        return ScopedContainer(self)
    
    def is_registered(self, service_type: Type) -> bool:
        """Проверяет, зарегистрирован ли сервис."""
        return service_type in self._services


class ScopedContainer:
    """
    Scoped контейнер для изоляции сервисов в рамках одной области видимости.
    
    Используется для изоляции тестовых сессий - каждый тест выполняется
    в своем scope'е, что гарантирует отсутствие влияния между тестами.
    """
    
    def __init__(self, parent: DependencyContainer):
        self._parent = parent
        self._scoped_instances: Dict[Type, Any] = {}
        self._disposed = False
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Разрешает зависимость в scoped контексте.
        
        Args:
            service_type: Тип запрашиваемого сервиса
            
        Returns:
            Экземпляр сервиса
        """
        if self._disposed:
            raise DependencyResolutionError("Cannot resolve services from disposed scope")
        
        if service_type not in self._parent._services:
            raise DependencyResolutionError(f"Service {service_type.__name__} is not registered")
        
        descriptor = self._parent._services[service_type]
        
        # Scoped сервисы - один экземпляр на scope
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            if service_type in self._scoped_instances:
                return self._scoped_instances[service_type]
            
            instance = self._parent._create_instance(descriptor)
            self._scoped_instances[service_type] = instance
            return instance
        
        # Остальные сервисы делегируем родительскому контейнеру
        else:
            return self._parent.resolve(service_type)
    
    def dispose(self) -> None:
        """
        Освобождает ресурсы scope'а.
        
        Вызывает dispose() у всех scoped сервисов, которые его поддерживают.
        """
        if self._disposed:
            return
        
        # Вызываем dispose у сервисов, которые его поддерживают
        for instance in self._scoped_instances.values():
            if hasattr(instance, 'dispose') and callable(getattr(instance, 'dispose')):
                try:
                    instance.dispose()
                except Exception:
                    # Игнорируем ошибки при dispose - не должны ломать cleanup
                    pass
        
        self._scoped_instances.clear()
        self._disposed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()


class IDisposable(ABC):
    """Интерфейс для объектов, которые требуют явного освобождения ресурсов."""
    
    @abstractmethod
    def dispose(self) -> None:
        """Освобождает ресурсы объекта."""
        pass