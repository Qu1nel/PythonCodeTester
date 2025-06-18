"""Defines custom exceptions for the code tester application.

These custom exception classes allow for more specific error handling and provide
clearer, more informative error messages throughout the testing framework.
"""


class CodeTesterError(Exception):
    """Base exception for all custom errors raised by this application."""
    pass


class TestCaseError(CodeTesterError):
    """Raised when a test case JSON file is malformed or invalid.

    This error indicates a problem with the configuration of a test case or
    one of its checks, not with the code being tested.

    Attributes:
        check_id (int | str | None): The ID of the check that caused the error,
            if available.
    """

    def __init__(self, message: str, check_id: int | str | None = None):
        """Initializes the TestCaseError.

        Args:
            message: The specific error message describing the problem.
            check_id: The ID of the problematic check.
        """
        self.check_id = check_id
        if check_id:
            super().__init__(f"Error in test check '{check_id}': {message}")
        else:
            super().__init__(f"Error in test case file: {message}")


class TestCheckError(CodeTesterError):
    """Raised when an error occurs during the execution of a single check.

    This typically indicates a problem with the test setup or the student's
    code that prevents the check from completing, such as a `ModuleNotFoundError`
    when trying to import a function.
    """
    pass