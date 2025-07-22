"""Execution environment for isolated test execution."""

import io
import sys
import uuid
from contextlib import contextmanager
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

from ..config import LogLevel
from ..utils.exceptions import SolutionImportError
from ..logging import Console, log_initialization


class ExecutionEnvironment:
    """Manages isolated execution environment for solution code."""
    
    @log_initialization(level=LogLevel.TRACE)
    def __init__(self, solution_path: Path, console: Console):
        """Initialize execution environment.
        
        Args:
            solution_path: Path to the solution file to execute
            console: Console instance for logging
        """
        self._solution_path = solution_path
        self._console = console
        self._module: ModuleType | None = None
        self._console.print(f"Environment created for: {self._solution_path}", level=LogLevel.DEBUG)

    def _import_solution_module(self) -> ModuleType:
        """Import solution module with unique name to avoid conflicts.
        
        Returns:
            Imported module instance
            
        Raises:
            FileNotFoundError: If solution file doesn't exist
            SolutionImportError: If import fails
        """
        if not self._solution_path.exists():
            raise FileNotFoundError(f"Solution file not found: {self._solution_path}")

        try:
            unique_module_name = f"solution_{self._solution_path.stem}_{uuid.uuid4().hex}"
            self._console.print(f"Importing solution as '{unique_module_name}'", level=LogLevel.DEBUG)

            spec = spec_from_file_location(unique_module_name, self._solution_path)
            if not spec or not spec.loader:
                raise ImportError("Could not create module spec from file.")

            module = module_from_spec(spec)
            sys.modules[unique_module_name] = module
            spec.loader.exec_module(module)

            self._console.print(f"Module '{unique_module_name}' imported successfully.", level=LogLevel.DEBUG)
            return module
        except Exception as e:
            raise SolutionImportError(str(e), path=self._solution_path) from e

    @contextmanager
    def run_in_isolation(self, stdin_text: str | None = None):
        """Context manager for isolated execution with captured I/O.
        
        Args:
            stdin_text: Optional stdin input for the solution
            
        Yields:
            Tuple of (module, captured_output) where captured_output is dict with 'stdout' and 'stderr'
        """
        self._console.print("Entering isolated I/O context.", level=LogLevel.TRACE)
        if stdin_text:
            self._console.print(
                'Providing stdin: "{}"...'.format(stdin_text[:50].replace("\n", "\\n")), level=LogLevel.TRACE
            )

        original_stdin, original_stdout, original_stderr = sys.stdin, sys.stdout, sys.stderr

        # noinspection PyTypeChecker
        stdout_wrapper = io.TextIOWrapper(io.BytesIO(), encoding=sys.stdout.encoding)
        # noinspection PyTypeChecker
        stderr_wrapper = io.TextIOWrapper(io.BytesIO(), encoding=sys.stderr.encoding)

        sys.stdout = stdout_wrapper
        sys.stderr = stderr_wrapper
        sys.stdin = io.StringIO(stdin_text or "")

        captured_output = {"stdout": "", "stderr": ""}

        try:
            self._module = self._import_solution_module()
            yield self._module, captured_output
        finally:
            sys.stdout.flush()
            sys.stderr.flush()

            stdout_wrapper.seek(0)
            stderr_wrapper.seek(0)
            captured_output["stdout"] = stdout_wrapper.read()
            captured_output["stderr"] = stderr_wrapper.read()

            sys.stdin, sys.stdout, sys.stderr = original_stdin, original_stdout, original_stderr
            self._console.print("Exited isolated I/O context.", level=LogLevel.TRACE)

            if self._module and self._module.__name__ in sys.modules:
                del sys.modules[self._module.__name__]
                self._console.print(f"Unloaded module '{self._module.__name__}'.", level=LogLevel.DEBUG)

            self._module = None