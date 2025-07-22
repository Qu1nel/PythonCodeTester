class CustomError(Exception):
    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code


class ValidationError(CustomError):
    pass


def divide_numbers(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def validate_age(age: int) -> bool:
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValidationError("Age seems unrealistic", code=1001)
    return True


def access_list_item(items: list, index: int):
    if not items:
        raise CustomError("List is empty", code=2001)
    return items[index]


def parse_number(value: str) -> int:
    if not value:
        raise ValueError("Empty string cannot be parsed")
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f"Cannot parse '{value}' as integer") from e


class ResourceManager:
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.is_open = False
    
    def open(self) -> None:
        if self.is_open:
            raise RuntimeError(f"Resource {self.resource_name} is already open")
        self.is_open = True
    
    def close(self) -> None:
        if not self.is_open:
            raise RuntimeError(f"Resource {self.resource_name} is not open")
        self.is_open = False
    
    def read_data(self) -> str:
        if not self.is_open:
            raise RuntimeError("Cannot read from closed resource")
        return f"Data from {self.resource_name}"