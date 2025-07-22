"""Custom exceptions for the code tester framework."""

from pathlib import Path


class CodeTesterError(Exception):
    """Base exception for all code tester errors."""
    pass


class ExecutionError(CodeTesterError):
    """Base exception for execution-related errors."""
    pass


class ConfigError(CodeTesterError):
    """Base exception for configuration-related errors."""
    
    def __init__(self, message: str, *, path: Path):
        self.path = path
        super().__init__(f"{message} (in file: {path})")


class TestCaseParsingError(ConfigError):
    """Exception raised when parsing test case configuration fails."""
    
    def __init__(self, message: str, *, path: Path = None, check_id: int | None = None):
        self.check_id = check_id
        if check_id:
            message = f"Error in test case file {path}. Error parsing check '{check_id}': {message}"
        super().__init__(message, path=path)


class SolutionImportError(ExecutionError):
    """Exception raised when importing solution file fails."""
    
    def __init__(self, message: str, *, path: Path):
        self.path = path
        super().__init__(f"Failed to import solution file '{path}': {message}")


class ActionError(ExecutionError):
    """Exception raised when action execution fails."""
    
    def __init__(self, message: str, *, check_id: int, action: str):
        self.check_id = check_id
        self.action = action
        super().__init__(f"Error during execution of action '{action}' in check '{check_id}': {message}")


# Исключения для DI контейнера
class DependencyResolutionError(CodeTesterError):
    """Ошибка разрешения зависимости в DI контейнере."""
    pass


class CircularDependencyError(DependencyResolutionError):
    """Ошибка циклической зависимости в DI контейнере."""
    pass


# Исключения для валидации
class ValidationError(CodeTesterError):
    """Ошибка валидации конфигурации."""
    pass


# Исключения для плагинов
class PluginError(CodeTesterError):
    """Ошибка загрузки или работы плагина."""
    pass


# Переименовываем AssertionError чтобы избежать конфликта с встроенным
class AssertionError(ExecutionError):
    """Exception raised when assertion fails."""
    pass