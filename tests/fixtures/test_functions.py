
def add(a, b):
    return a + b

def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
