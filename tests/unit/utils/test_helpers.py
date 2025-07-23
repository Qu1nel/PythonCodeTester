import pytest
from pydantic import BaseModel

from code_tester.utils import create_dataclass_from_dict, create_pydantic_from_dict


class TestHelpers:
    def test_create_pydantic_from_dict_simple(self):
        class Simple(BaseModel):
            name: str
            age: int

        data = {"name": "John", "age": 30, "extra": "ignored"}
        result = create_pydantic_from_dict(Simple, data)
        
        assert result.name == "John"
        assert result.age == 30
        assert not hasattr(result, "extra")

    def test_create_pydantic_from_dict_nested(self):
        class Address(BaseModel):
            street: str
            city: str

        class Person(BaseModel):
            name: str
            address: Address

        data = {
            "name": "John",
            "address": {"street": "123 Main St", "city": "Anytown"}
        }
        result = create_pydantic_from_dict(Person, data)
        
        assert result.name == "John"
        assert isinstance(result.address, Address)
        assert result.address.street == "123 Main St"
        assert result.address.city == "Anytown"

    def test_create_pydantic_from_dict_list(self):
        class Item(BaseModel):
            id: int
            name: str

        class Container(BaseModel):
            items: list[Item]

        data = {
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"}
            ]
        }
        result = create_pydantic_from_dict(Container, data)
        
        assert len(result.items) == 2
        assert all(isinstance(item, Item) for item in result.items)
        assert result.items[0].id == 1
        assert result.items[1].name == "Item 2"

    def test_create_pydantic_from_dict_non_pydantic_raises_error(self):
        class NotPydantic:
            pass

        with pytest.raises(TypeError) as exc_info:
            create_pydantic_from_dict(NotPydantic, {})
        
        assert "is not a pydantic BaseModel" in str(exc_info.value)

    def test_create_dataclass_from_dict_is_alias(self):
        class Simple(BaseModel):
            name: str

        data = {"name": "test"}
        result1 = create_dataclass_from_dict(Simple, data)
        result2 = create_pydantic_from_dict(Simple, data)
        
        assert result1.name == result2.name
        assert type(result1) == type(result2)