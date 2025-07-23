import unittest
from unittest.mock import Mock

from code_tester.core import (
    DependencyContainer,
    ComponentMetadata,
    ComponentProvider,
    PluginManager,
    PluginRegistry,
    plugin_provider,
)
from code_tester.utils.exceptions import PluginError


class TestComponentProvider(ComponentProvider):
    def __init__(self, name: str, version: str = "1.0.0", test_types: list[str] = None, dependencies: list[str] = None):
        self._metadata = ComponentMetadata(
            name=name,
            version=version,
            test_types=test_types or ["py_general"],
            dependencies=dependencies or []
        )
        self.register_called = False
    
    @property
    def metadata(self) -> ComponentMetadata:
        return self._metadata
    
    def register_components(self, container: DependencyContainer) -> None:
        self.register_called = True


class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.container = DependencyContainer()
        self.plugin_manager = PluginManager(self.container)
    
    def test_register_plugin(self):
        provider = TestComponentProvider("test_plugin")
        
        self.plugin_manager.register_plugin(provider)
        
        self.assertIn("test_plugin", self.plugin_manager._plugins)
        descriptor = self.plugin_manager._plugins["test_plugin"]
        self.assertEqual(descriptor.name, "test_plugin")
        self.assertIs(descriptor.provider, provider)
        self.assertFalse(descriptor.is_loaded)
    
    def test_register_duplicate_plugin_raises_error(self):
        provider1 = TestComponentProvider("test_plugin")
        provider2 = TestComponentProvider("test_plugin")
        
        self.plugin_manager.register_plugin(provider1)
        
        with self.assertRaises(PluginError) as context:
            self.plugin_manager.register_plugin(provider2)
        
        self.assertIn("already registered", str(context.exception))
    
    def test_load_plugin(self):
        provider = TestComponentProvider("test_plugin")
        self.plugin_manager.register_plugin(provider)
        
        self.plugin_manager.load_plugin("test_plugin")
        
        self.assertTrue(provider.register_called)
        descriptor = self.plugin_manager._plugins["test_plugin"]
        self.assertTrue(descriptor.is_loaded)
        self.assertIn("test_plugin", self.plugin_manager._loaded_order)
    
    def test_load_nonexistent_plugin_raises_error(self):
        with self.assertRaises(PluginError) as context:
            self.plugin_manager.load_plugin("nonexistent")
        
        self.assertIn("is not registered", str(context.exception))
    
    def test_load_plugin_twice_does_nothing(self):
        provider = TestComponentProvider("test_plugin")
        self.plugin_manager.register_plugin(provider)
        
        self.plugin_manager.load_plugin("test_plugin")
        provider.register_called = False
        self.plugin_manager.load_plugin("test_plugin")
        
        self.assertFalse(provider.register_called)
    
    def test_load_plugin_with_dependencies(self):
        dependency_provider = TestComponentProvider("dependency")
        main_provider = TestComponentProvider("main", dependencies=["dependency"])
        
        self.plugin_manager.register_plugin(dependency_provider)
        self.plugin_manager.register_plugin(main_provider)
        
        self.plugin_manager.load_plugin("main")
        
        self.assertTrue(dependency_provider.register_called)
        self.assertTrue(main_provider.register_called)
        self.assertEqual(self.plugin_manager._loaded_order, ["dependency", "main"])
    
    def test_load_plugin_with_missing_dependency_raises_error(self):
        provider = TestComponentProvider("main", dependencies=["missing"])
        self.plugin_manager.register_plugin(provider)
        
        with self.assertRaises(PluginError) as context:
            self.plugin_manager.load_plugin("main")
        
        self.assertIn("depends on 'missing'", str(context.exception))
    
    def test_load_all_plugins(self):
        provider1 = TestComponentProvider("plugin1")
        provider2 = TestComponentProvider("plugin2")
        
        self.plugin_manager.register_plugin(provider1)
        self.plugin_manager.register_plugin(provider2)
        
        self.plugin_manager.load_all_plugins()
        
        self.assertTrue(provider1.register_called)
        self.assertTrue(provider2.register_called)
    
    def test_get_providers_for_test_type(self):
        provider1 = TestComponentProvider("plugin1", test_types=["py_general"])
        provider2 = TestComponentProvider("plugin2", test_types=["flask"])
        provider3 = TestComponentProvider("plugin3", test_types=["py_general", "flask"])
        
        self.plugin_manager.register_plugin(provider1)
        self.plugin_manager.register_plugin(provider2)
        self.plugin_manager.register_plugin(provider3)
        
        self.plugin_manager.load_all_plugins()
        
        py_providers = self.plugin_manager.get_providers_for_test_type("py_general")
        flask_providers = self.plugin_manager.get_providers_for_test_type("flask")
        
        self.assertEqual(len(py_providers), 2)
        self.assertIn(provider1, py_providers)
        self.assertIn(provider3, py_providers)
        
        self.assertEqual(len(flask_providers), 2)
        self.assertIn(provider2, flask_providers)
        self.assertIn(provider3, flask_providers)
    
    def test_get_providers_for_test_type_only_loaded(self):
        provider1 = TestComponentProvider("plugin1", test_types=["py_general"])
        provider2 = TestComponentProvider("plugin2", test_types=["py_general"])
        
        self.plugin_manager.register_plugin(provider1)
        self.plugin_manager.register_plugin(provider2)
        
        self.plugin_manager.load_plugin("plugin1")
        
        providers = self.plugin_manager.get_providers_for_test_type("py_general")
        
        self.assertEqual(len(providers), 1)
        self.assertIn(provider1, providers)
        self.assertNotIn(provider2, providers)


class TestPluginRegistry(unittest.TestCase):
    def setUp(self):
        PluginRegistry._instance = None
    
    def test_singleton_pattern(self):
        registry1 = PluginRegistry()
        registry2 = PluginRegistry()
        
        self.assertIs(registry1, registry2)
    
    def test_register_and_get_providers(self):
        registry = PluginRegistry()
        provider = TestComponentProvider("test")
        
        registry.register(provider)
        providers = registry.get_all_providers()
        
        self.assertEqual(len(providers), 1)
        self.assertIn(provider, providers)
    
    def test_clear(self):
        registry = PluginRegistry()
        provider = TestComponentProvider("test")
        
        registry.register(provider)
        registry.clear()
        providers = registry.get_all_providers()
        
        self.assertEqual(len(providers), 0)


class TestPluginProviderDecorator(unittest.TestCase):
    def setUp(self):
        PluginRegistry._instance = None
    
    def test_plugin_provider_decorator(self):
        metadata = ComponentMetadata(
            name="test_plugin",
            version="1.0.0",
            test_types=["py_general"]
        )
        
        @plugin_provider(metadata)
        class TestProvider(ComponentProvider):
            def register_components(self, container: DependencyContainer) -> None:
                pass
        
        registry = PluginRegistry()
        providers = registry.get_all_providers()
        
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].metadata.name, "test_plugin")
        self.assertEqual(providers[0].metadata.version, "1.0.0")


if __name__ == '__main__':
    unittest.main()