import unittest
from pathlib import Path

from src.code_tester.exceptions import (
    ActionError,
    SolutionImportError,
    TestCaseParsingError,
)


class TestCustomExceptions(unittest.TestCase):
    def test_test_case_parsing_error_formats_correctly(self):
        path = Path("test/rules.json")
        err1 = TestCaseParsingError("Missing 'checks' key", path=path, check_id=1)
        self.assertIn("Error in test case file", str(err1))
        self.assertIn(str(path), str(err1))

        err2 = TestCaseParsingError("Unknown action", path=path, check_id=5)
        self.assertIn("Error parsing check '5'", str(err2))

    def test_solution_import_error(self):
        path = Path("solution.py")
        err = SolutionImportError("SyntaxError", path=path)
        self.assertIn(f"Failed to import solution file '{path}'", str(err))

    def test_action_error(self):
        err = ActionError("Function not found", check_id=2, action="call_function")
        self.assertIn("Error during execution of action 'call_function'", str(err))
        self.assertIn("in check '2'", str(err))
