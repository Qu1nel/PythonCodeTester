"""Manages the isolated execution environment for student code.

This module provides context managers and utilities to safely import and run
student code while capturing its I/O streams (stdin, stdout, stderr).
"""

import io
import sys
from contextlib import contextmanager
from importlib import util as importlib_util
from pathlib import Path
from types import ModuleType

from .exceptions import TestCheckError


@contextmanager
def isolated_io(stdin_text: str | None = None):
    """A context manager to temporarily redirect I/O streams.

    Upon entering, it replaces sys.stdin, sys.stdout, and sys.stderr with
    in-memory text streams. Upon exiting, it restores the original streams.

    Args:
        stdin_text: The text to be fed into the new sys.stdin.

    Yields:
        A tuple containing the new stdout and stderr StringIO objects.
    """
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    sys.stdin = io.StringIO(stdin_text or "")
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    try:
        yield sys.stdout, sys.stderr
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def import_solution_module(path: Path) -> ModuleType:
    """Safely imports a Python source file as an isolated module.

    Args:
        path: The path to the Python file.

    Returns:
        The imported module object.

    Raises:
        TestCheckError: If the file cannot be imported.
    """
    try:
        module_name = path.stem
        spec = importlib_util.spec_from_file_location(module_name, path)
        if not spec or not spec.loader:
            raise ImportError("Could not create module spec.")

        module = importlib_util.module_from_spec(spec)
        sys.modules[module_name] = module  # Добавляем его в sys.modules для возможных кейсов проверки на рекурсию
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise TestCheckError(f"Failed to import solution file '{path}': {e}") from e
