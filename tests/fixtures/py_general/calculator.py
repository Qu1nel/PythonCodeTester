class Calculator:
    def __init__(self, initial_value: float = 0.0):
        self.value = initial_value
        self.history = []
    
    def add(self, x: float) -> float:
        self.value += x
        self.history.append(f"add({x})")
        return self.value
    
    def subtract(self, x: float) -> float:
        self.value -= x
        self.history.append(f"subtract({x})")
        return self.value
    
    def multiply(self, x: float) -> float:
        self.value *= x
        self.history.append(f"multiply({x})")
        return self.value
    
    def divide(self, x: float) -> float:
        if x == 0:
            raise ValueError("Cannot divide by zero")
        self.value /= x
        self.history.append(f"divide({x})")
        return self.value
    
    def reset(self) -> None:
        self.value = 0.0
        self.history.clear()
    
    def get_history(self) -> list[str]:
        return self.history.copy()


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True