import unittest

from code_tester.execution import ExecutionContext, ObjectStore


class TestExecutionContext(unittest.TestCase):
    def setUp(self):
        self.context = ExecutionContext()

    def test_save_and_get_object(self):
        obj = {"test": "value"}
        self.context.save_object("test_obj", obj)
        
        retrieved = self.context.get_object("test_obj")
        self.assertEqual(retrieved, obj)

    def test_has_object(self):
        self.assertFalse(self.context.has_object("nonexistent"))
        
        self.context.save_object("test_obj", "value")
        self.assertTrue(self.context.has_object("test_obj"))

    def test_get_nonexistent_object_raises_error(self):
        with self.assertRaises(KeyError):
            self.context.get_object("nonexistent")

    def test_save_and_get_variable(self):
        self.context.save_variable("test_var", 42)
        
        retrieved = self.context.get_variable("test_var")
        self.assertEqual(retrieved, 42)

    def test_has_variable(self):
        self.assertFalse(self.context.has_variable("nonexistent"))
        
        self.context.save_variable("test_var", "value")
        self.assertTrue(self.context.has_variable("test_var"))

    def test_get_nonexistent_variable_raises_error(self):
        with self.assertRaises(KeyError):
            self.context.get_variable("nonexistent")

    def test_clear(self):
        self.context.save_object("obj", "value")
        self.context.save_variable("var", "value")
        
        self.context.clear()
        
        self.assertFalse(self.context.has_object("obj"))
        self.assertFalse(self.context.has_variable("var"))

    def test_get_all_objects(self):
        self.context.save_object("obj1", "value1")
        self.context.save_object("obj2", "value2")
        
        all_objects = self.context.get_all_objects()
        
        self.assertEqual(all_objects, {"obj1": "value1", "obj2": "value2"})

    def test_get_all_variables(self):
        self.context.save_variable("var1", "value1")
        self.context.save_variable("var2", "value2")
        
        all_variables = self.context.get_all_variables()
        
        self.assertEqual(all_variables, {"var1": "value1", "var2": "value2"})


class TestObjectStore(unittest.TestCase):
    def setUp(self):
        self.store = ObjectStore()

    def test_store_and_retrieve(self):
        self.store.store("key1", "value1")
        
        retrieved = self.store.retrieve("key1")
        self.assertEqual(retrieved, "value1")

    def test_store_with_type_hint(self):
        self.store.store("key1", "value1", "str")
        
        retrieved = self.store.retrieve("key1")
        type_hint = self.store.get_type_hint("key1")
        
        self.assertEqual(retrieved, "value1")
        self.assertEqual(type_hint, "str")

    def test_exists(self):
        self.assertFalse(self.store.exists("nonexistent"))
        
        self.store.store("key1", "value1")
        self.assertTrue(self.store.exists("key1"))

    def test_retrieve_nonexistent_raises_error(self):
        with self.assertRaises(KeyError):
            self.store.retrieve("nonexistent")

    def test_get_type_hint_nonexistent_returns_none(self):
        type_hint = self.store.get_type_hint("nonexistent")
        self.assertIsNone(type_hint)

    def test_remove(self):
        self.store.store("key1", "value1", "str")
        
        self.store.remove("key1")
        
        self.assertFalse(self.store.exists("key1"))
        self.assertIsNone(self.store.get_type_hint("key1"))

    def test_remove_nonexistent_does_nothing(self):
        # Should not raise an error
        self.store.remove("nonexistent")

    def test_clear(self):
        self.store.store("key1", "value1", "str")
        self.store.store("key2", "value2", "str")
        
        self.store.clear()
        
        self.assertFalse(self.store.exists("key1"))
        self.assertFalse(self.store.exists("key2"))

    def test_keys(self):
        self.store.store("key1", "value1")
        self.store.store("key2", "value2")
        
        keys = self.store.keys()
        
        self.assertEqual(set(keys), {"key1", "key2"})

    def test_values(self):
        self.store.store("key1", "value1")
        self.store.store("key2", "value2")
        
        values = self.store.values()
        
        self.assertEqual(set(values), {"value1", "value2"})

    def test_items(self):
        self.store.store("key1", "value1")
        self.store.store("key2", "value2")
        
        items = self.store.items()
        
        self.assertEqual(set(items), {("key1", "value1"), ("key2", "value2")})


if __name__ == '__main__':
    unittest.main()