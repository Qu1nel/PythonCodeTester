import dataclasses
from typing import Any, Type, TypeVar, Union, get_args, get_origin

T = TypeVar("T")


def create_dataclass_from_dict(cls: Type[T], data: dict[str, Any]) -> T:
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"Target class {cls.__name__} is not a dataclass.")

    init_kwargs = {}

    class_fields = {f.name: f.type for f in dataclasses.fields(cls)}

    for field_name, field_type in class_fields.items():
        if field_name not in data:
            continue

        value = data[field_name]
        origin_type = get_origin(field_type)
        type_args = get_args(field_type)

        if origin_type is Union:
            for potential_type in type_args:
                if potential_type is type(None) and value is None:
                    init_kwargs[field_name] = None
                    break
                try:
                    init_kwargs[field_name] = create_dataclass_from_dict(potential_type, value)
                    break
                except (TypeError, ValueError):
                    continue
            else:
                init_kwargs[field_name] = value

        elif origin_type in (list, tuple, set) and type_args:
            inner_type = type_args[0]
            if dataclasses.is_dataclass(inner_type):
                init_kwargs[field_name] = [create_dataclass_from_dict(inner_type, item) for item in value]
            else:
                init_kwargs[field_name] = value

        elif dataclasses.is_dataclass(field_type):
            init_kwargs[field_name] = create_dataclass_from_dict(field_type, value)

        else:
            init_kwargs[field_name] = value

    return cls(**init_kwargs)
