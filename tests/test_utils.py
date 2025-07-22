import unittest

from pydantic import BaseModel

from code_tester.utils import create_dataclass_from_dict


class TestCreateDataclassFromDict(unittest.TestCase):
    def test_simple_pydantic_model(self):
        class Simple(BaseModel):
            a: int
            b: str

        data = {"a": 1, "b": "test", "c": "extra"}
        instance = create_dataclass_from_dict(Simple, data)
        self.assertEqual(instance.a, 1)
        self.assertEqual(instance.b, "test")
        self.assertFalse(hasattr(instance, "c"))

    def test_nested_pydantic_model(self):
        class Inner(BaseModel):
            x: int

        class Outer(BaseModel):
            inner_obj: Inner
            name: str

        data = {"name": "outer", "inner_obj": {"x": 100}}
        instance = create_dataclass_from_dict(Outer, data)
        self.assertEqual(instance.name, "outer")
        self.assertIsInstance(instance.inner_obj, Inner)
        self.assertEqual(instance.inner_obj.x, 100)

    def test_list_of_pydantic_models(self):
        class Item(BaseModel):
            id: int

        class Container(BaseModel):
            items: list[Item]

        data = {"items": [{"id": 1}, {"id": 2}]}
        instance = create_dataclass_from_dict(Container, data)
        self.assertEqual(len(instance.items), 2)
        self.assertIsInstance(instance.items[0], Item)
        self.assertEqual(instance.items[1].id, 2)

    def test_raises_error_for_non_pydantic_model(self):
        class NotAPydanticModel:
            pass

        with self.assertRaises(TypeError):
            create_dataclass_from_dict(NotAPydanticModel, {})
