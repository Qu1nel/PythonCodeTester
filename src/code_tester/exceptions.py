from pathlib import Path


class CodeTesterError(Exception):
    pass


class ExecutionError(CodeTesterError):
    pass


class ConfigError(CodeTesterError):
    def __init__(self, message: str, *, path: Path):
        self.path = path
        super().__init__(f"{message} (in file: {path})")


class TestCaseParsingError(ConfigError):
    def __init__(self, message: str, *, path: Path = None, check_id: int | None = None):
        self.check_id = check_id
        if check_id:
            message = f"Error in test case file {path}. Error parsing check '{check_id}': {message}"
        super().__init__(message, path=path)


class SolutionImportError(ExecutionError):
    def __init__(self, message: str, *, path: Path):
        self.path = path
        super().__init__(f"Failed to import solution file '{path}': {message}")


class ActionError(ExecutionError):
    def __init__(self, message: str, *, check_id: int, action: str):
        self.check_id = check_id
        self.action = action
        super().__init__(f"Error during execution of action '{action}' in check '{check_id}': {message}")
