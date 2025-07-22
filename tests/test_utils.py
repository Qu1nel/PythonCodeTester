import unittest
from dataclasses import dataclass

from src.code_tester.utils import create_dataclass_from_dict


class TestCreateDataclassFromDict(unittest.TestCase):
    def test_simple_dataclass(self):
        @dataclass
        class Simple:
            a: int
            b: str

        data = {"a": 1, "b": "test", "c": "extra"}
        instance = create_dataclass_from_dict(Simple, data)
        self.assertEqual(instance.a, 1)
        self.assertEqual(instance.b, "test")
        self.assertFalse(hasattr(instance, "c"))

    def test_nested_dataclass(self):
        @dataclass
        class Inner:
            x: int

        @dataclass
        class Outer:
            inner_obj: Inner
            name: str

        data = {"name": "outer", "inner_obj": {"x": 100}}
        instance = create_dataclass_from_dict(Outer, data)
        self.assertEqual(instance.name, "outer")
        self.assertIsInstance(instance.inner_obj, Inner)
        self.assertEqual(instance.inner_obj.x, 100)

    def test_list_of_dataclasses(self):
        @dataclass
        class Item:
            id: int

        @dataclass
        class Container:
            items: list[Item]

        data = {"items": [{"id": 1}, {"id": 2}]}
        instance = create_dataclass_from_dict(Container, data)
        self.assertEqual(len(instance.items), 2)
        self.assertIsInstance(instance.items[0], Item)
        self.assertEqual(instance.items[1].id, 2)

    def test_raises_error_for_non_dataclass(self):
        class NotADataclass:
            pass

        with self.assertRaises(TypeError):
            create_dataclass_from_dict(NotADataclass, {})
