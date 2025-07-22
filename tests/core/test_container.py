"""
Unit тесты для DependencyContainer.

Тестируют все аспекты IoC контейнера:
- Регистрацию сервисов (singleton, transient, scoped)
- Разрешение зависимостей
- Автоматическое внедрение зависимостей
- Обнаружение циклических зависимостей
- Работу с scoped контейнерами
"""

import unittest
from unittest.mock import Mock

from code_tester.core import (
    DependencyContainer,
    ScopedContainer,
    ServiceLifetime,
    IDisposable,
)
from code_tester.utils.exceptions import (
    DependencyResolutionError,
    CircularDependencyError,
)


# Тестовые классы для проверки DI
class ITestService:
    """Интерфейс тестового сервиса."""
    def get_value(self) -> str:
        pass


class TestService(ITestService):
    """Простая реализация тестового сервиса."""
    def __init__(self):
        self.created_count = 1
    
    def get_value(self) -> str:
        return "test_value"


class TestServiceWithDependency(ITestService):
    """Сервис с зависимостью."""
    def __init__(self, dependency: ITestService):
        self.dependency = dependency
    
    def get_value(self) -> str:
        return f"dependent_{self.dependency.get_value()}"


class TestServiceWithMultipleDependencies:
    """Сервис с несколькими зависимостями."""
    def __init__(self, service1: ITestService, service2: TestService):
        self.service1 = service1
        self.service2 = service2


class DisposableService(IDisposable):
    """Сервис, требующий освобождения ресурсов."""
    def __init__(self):
        self.disposed = False
    
    def dispose(self) -> None:
        self.disposed = True


class CircularDependencyA:
    """Класс для тестирования циклических зависимостей."""
    def __init__(self, b):  # Убираем type hint для простоты
        self.b = b


class CircularDependencyB:
    """Класс для тестирования циклических зависимостей."""
    def __init__(self, a: CircularDependencyA):
        self.a = a


class TestDependencyContainer(unittest.TestCase):
    """Тесты для DependencyContainer."""
    
    def setUp(self):
        self.container = DependencyContainer()
    
    def test_register_and_resolve_singleton(self):
        """Тест регистрации и разрешения singleton сервиса."""
        # Arrange
        self.container.register_singleton(ITestService, TestService)
        
        # Act
        instance1 = self.container.resolve(ITestService)
        instance2 = self.container.resolve(ITestService)
        
        # Assert
        self.assertIsInstance(instance1, TestService)
        self.assertIsInstance(instance2, TestService)
        self.assertIs(instance1, instance2)  # Должен быть тот же экземпляр
    
    def test_register_and_resolve_transient(self):
        """Тест регистрации и разрешения transient сервиса."""
        # Arrange
        self.container.register_transient(ITestService, TestService)
        
        # Act
        instance1 = self.container.resolve(ITestService)
        instance2 = self.container.resolve(ITestService)
        
        # Assert
        self.assertIsInstance(instance1, TestService)
        self.assertIsInstance(instance2, TestService)
        self.assertIsNot(instance1, instance2)  # Должны быть разные экземпляры
    
    def test_register_instance(self):
        """Тест регистрации готового экземпляра."""
        # Arrange
        instance = TestService()
        self.container.register_instance(ITestService, instance)
        
        # Act
        resolved = self.container.resolve(ITestService)
        
        # Assert
        self.assertIs(resolved, instance)
    
    def test_register_factory(self):
        """Тест регистрации фабричной функции."""
        # Arrange
        def factory() -> ITestService:
            service = TestService()
            service.created_count = 42
            return service
        
        self.container.register_factory(ITestService, factory)
        
        # Act
        instance = self.container.resolve(ITestService)
        
        # Assert
        self.assertIsInstance(instance, TestService)
        self.assertEqual(instance.created_count, 42)
    
    def test_dependency_injection(self):
        """Тест автоматического внедрения зависимостей."""
        # Arrange
        self.container.register_singleton(ITestService, TestService)
        
        # Используем фабрику для явного создания с зависимостью
        def create_service_with_dependency() -> TestServiceWithDependency:
            dependency = self.container.resolve(ITestService)
            return TestServiceWithDependency(dependency)
        
        self.container.register_factory(TestServiceWithDependency, create_service_with_dependency)
        
        # Act
        instance = self.container.resolve(TestServiceWithDependency)
        
        # Assert
        self.assertIsInstance(instance, TestServiceWithDependency)
        self.assertIsInstance(instance.dependency, TestService)
        self.assertEqual(instance.get_value(), "dependent_test_value")
    
    def test_multiple_dependencies(self):
        """Тест внедрения нескольких зависимостей."""
        # Arrange
        self.container.register_singleton(ITestService, TestService)
        self.container.register_transient(TestService, TestService)
        
        # Используем фабрику для явного создания с несколькими зависимостями
        def create_service_with_multiple_dependencies() -> TestServiceWithMultipleDependencies:
            service1 = self.container.resolve(ITestService)
            service2 = self.container.resolve(TestService)
            return TestServiceWithMultipleDependencies(service1, service2)
        
        self.container.register_factory(TestServiceWithMultipleDependencies, create_service_with_multiple_dependencies)
        
        # Act
        instance = self.container.resolve(TestServiceWithMultipleDependencies)
        
        # Assert
        self.assertIsInstance(instance.service1, TestService)
        self.assertIsInstance(instance.service2, TestService)
        # service1 должен быть singleton, service2 - transient
        self.assertIs(instance.service1, self.container.resolve(ITestService))
        self.assertIsNot(instance.service2, self.container.resolve(TestService))
    
    def test_unregistered_service_throws_error(self):
        """Тест ошибки при запросе незарегистрированного сервиса."""
        with self.assertRaises(DependencyResolutionError) as context:
            self.container.resolve(ITestService)
        
        self.assertIn("is not registered", str(context.exception))
    
    def test_circular_dependency_detection(self):
        """Тест обнаружения циклических зависимостей."""
        # Arrange - создаем фабрики, которые будут создавать циклические зависимости
        def create_a() -> CircularDependencyA:
            b = self.container.resolve(CircularDependencyB)
            return CircularDependencyA(b)
        
        def create_b() -> CircularDependencyB:
            a = self.container.resolve(CircularDependencyA)
            return CircularDependencyB(a)
        
        self.container.register_factory(CircularDependencyA, create_a)
        self.container.register_factory(CircularDependencyB, create_b)
        
        # Act & Assert
        with self.assertRaises(CircularDependencyError) as context:
            self.container.resolve(CircularDependencyA)
        
        self.assertIn("Circular dependency detected", str(context.exception))
    
    def test_is_registered(self):
        """Тест проверки регистрации сервиса."""
        # Arrange
        self.container.register_singleton(ITestService, TestService)
        
        # Act & Assert
        self.assertTrue(self.container.is_registered(ITestService))
        self.assertFalse(self.container.is_registered(TestService))


class TestScopedContainer(unittest.TestCase):
    """Тесты для ScopedContainer."""
    
    def setUp(self):
        self.parent_container = DependencyContainer()
        self.scoped_container = self.parent_container.create_scope()
    
    def test_scoped_service_same_instance_within_scope(self):
        """Тест что scoped сервис возвращает тот же экземпляр в рамках scope."""
        # Arrange
        self.parent_container.register_scoped(ITestService, TestService)
        
        # Act
        instance1 = self.scoped_container.resolve(ITestService)
        instance2 = self.scoped_container.resolve(ITestService)
        
        # Assert
        self.assertIs(instance1, instance2)
    
    def test_scoped_service_different_instances_across_scopes(self):
        """Тест что scoped сервис возвращает разные экземпляры в разных scope."""
        # Arrange
        self.parent_container.register_scoped(ITestService, TestService)
        scope2 = self.parent_container.create_scope()
        
        # Act
        instance1 = self.scoped_container.resolve(ITestService)
        instance2 = scope2.resolve(ITestService)
        
        # Assert
        self.assertIsNot(instance1, instance2)
        
        # Cleanup
        scope2.dispose()
    
    def test_singleton_service_same_across_scopes(self):
        """Тест что singleton сервис одинаковый во всех scope."""
        # Arrange
        self.parent_container.register_singleton(ITestService, TestService)
        scope2 = self.parent_container.create_scope()
        
        # Act
        instance1 = self.scoped_container.resolve(ITestService)
        instance2 = scope2.resolve(ITestService)
        parent_instance = self.parent_container.resolve(ITestService)
        
        # Assert
        self.assertIs(instance1, instance2)
        self.assertIs(instance1, parent_instance)
        
        # Cleanup
        scope2.dispose()
    
    def test_transient_service_different_instances(self):
        """Тест что transient сервис возвращает разные экземпляры."""
        # Arrange
        self.parent_container.register_transient(ITestService, TestService)
        
        # Act
        instance1 = self.scoped_container.resolve(ITestService)
        instance2 = self.scoped_container.resolve(ITestService)
        
        # Assert
        self.assertIsNot(instance1, instance2)
    
    def test_dispose_calls_dispose_on_disposable_services(self):
        """Тест что dispose вызывается у disposable сервисов."""
        # Arrange
        self.parent_container.register_scoped(DisposableService, DisposableService)
        
        # Act
        service = self.scoped_container.resolve(DisposableService)
        self.assertFalse(service.disposed)
        
        self.scoped_container.dispose()
        
        # Assert
        self.assertTrue(service.disposed)
    
    def test_cannot_resolve_after_dispose(self):
        """Тест что нельзя разрешать сервисы после dispose."""
        # Arrange
        self.parent_container.register_scoped(ITestService, TestService)
        self.scoped_container.dispose()
        
        # Act & Assert
        with self.assertRaises(DependencyResolutionError) as context:
            self.scoped_container.resolve(ITestService)
        
        self.assertIn("disposed scope", str(context.exception))
    
    def test_context_manager(self):
        """Тест использования scoped контейнера как context manager."""
        # Arrange
        self.parent_container.register_scoped(DisposableService, DisposableService)
        
        # Act
        with self.parent_container.create_scope() as scope:
            service = scope.resolve(DisposableService)
            self.assertFalse(service.disposed)
        
        # Assert
        self.assertTrue(service.disposed)


if __name__ == '__main__':
    unittest.main()