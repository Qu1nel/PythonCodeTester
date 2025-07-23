import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.text import Text

from ..__version__ import __version__
from ..config import AppConfig, ExitCode
from ..execution import DynamicTester
from ..utils.exceptions import CodeTesterError
from ..logging import LogConfig, LogLevel, setup_logger, Console, generate_trace_id, set_trace_id

app = typer.Typer(
    name="code-tester",
    help="Dynamic testing framework for Python code using declarative JSON scenarios.",
    add_completion=False,
)

rich_console = RichConsole()


def version_callback(value: bool):
    if value:
        rich_console.print(f"[bold blue]code-tester[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.command()
def run(
    solution_path: Path = typer.Argument(
        ...,
        help="Path to the Python solution file to test",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    test_case_path: Path = typer.Argument(
        ...,
        help="Path to the JSON file with the test case",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.ERROR,
        "--log",
        "-l",
        help="Set the logging level",
        case_sensitive=False,
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all stdout output (test results and final verdict)",
    ),
    no_verdict: bool = typer.Option(
        False,
        "--no-verdict",
        help="Suppress final verdict, show only failed checks",
    ),
    max_messages: int = typer.Option(
        0,
        "--max-messages",
        "-m",
        help="Maximum number of failed check messages to display (0 for no limit)",
        min=0,
    ),
    exit_on_first_error: bool = typer.Option(
        False,
        "--exit-on-first-error",
        "-x",
        help="Exit instantly on the first failed check",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Execute a Python solution against a dynamic test case."""
    
    log_config = LogConfig(
        level=log_level,
        console_enabled=True,
        colorize=not quiet
    )
    logger = setup_logger(log_config)
    console = Console(logger, is_quiet=quiet, show_verdict=not no_verdict)
    
    trace_id = generate_trace_id()
    set_trace_id(trace_id)
    
    console.print(f"Logger configured with level: {log_level}", level=LogLevel.DEBUG)

    config = AppConfig(
        solution_path=solution_path,
        test_case_path=test_case_path,
        log_level=log_level,
        is_quiet=quiet,
        exit_on_first_error=exit_on_first_error,
        max_messages=max_messages,
    )
    console.print(f"Tester config: {config}", level=LogLevel.TRACE)

    try:
        if not quiet:
            rich_console.print(Panel(
                f"[bold]Testing:[/bold] {solution_path.name}\n"
                f"[bold]Test Case:[/bold] {test_case_path.name}",
                title="[bold blue]Code Tester[/bold blue]",
                border_style="blue"
            ))

        tester = DynamicTester(config, console)

        console.print("Running test case...", level=LogLevel.TRACE)
        all_passed = tester.run()
        console.print(f"Test case finished. Overall result: {all_passed}", level=LogLevel.TRACE)

        if all_passed:
            if not quiet:
                rich_console.print(Panel(
                    "[bold green]✅ All tests passed![/bold green]",
                    border_style="green"
                ))
            sys.exit(ExitCode.SUCCESS)
        else:
            failed_count = len(tester.failed_checks_ids)
            total_count = len(tester.test_case_config.checks) if tester.test_case_config else 0
            
            if not quiet:
                rich_console.print(Panel(
                    f"[bold red]❌ Some tests failed[/bold red]\n"
                    f"Failed: {failed_count} of {total_count}",
                    border_style="red"
                ))
            sys.exit(ExitCode.TESTS_FAILED)

    except CodeTesterError as e:
        rich_console.print(Panel(
            f"[bold red]Framework Error:[/bold red] {e}",
            border_style="red"
        ))
        sys.exit(ExitCode.TESTS_FAILED)
    except FileNotFoundError as e:
        rich_console.print(Panel(
            f"[bold red]File Not Found:[/bold red] {e.filename}",
            border_style="red"
        ))
        sys.exit(ExitCode.FILE_NOT_FOUND)
    except Exception as e:
        rich_console.print(Panel(
            f"[bold red]Unexpected Error:[/bold red] {e.__class__.__name__}\n"
            f"See logs for detailed traceback.",
            border_style="red"
        ))
        console.print(f"Exception details: {e}", level=LogLevel.CRITICAL, exc_info=True)
        sys.exit(ExitCode.UNEXPECTED_ERROR)


@app.command()
def validate(
    test_case_path: Path = typer.Argument(
        ...,
        help="Path to the JSON test case file to validate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    )
):
    """Validate a test case JSON file without executing it."""
    try:
        import json
        from ..utils import create_dataclass_from_dict
        from ..config import TestCaseConfig
        
        rich_console.print(f"[blue]Validating:[/blue] {test_case_path}")
        
        raw_data = json.loads(test_case_path.read_text("utf-8"))
        test_config = create_dataclass_from_dict(TestCaseConfig, raw_data)
        
        rich_console.print(Panel(
            f"[bold green]✅ Valid test case![/bold green]\n"
            f"[bold]Test ID:[/bold] {test_config.test_id}\n"
            f"[bold]Test Name:[/bold] {test_config.test_name}\n"
            f"[bold]Test Type:[/bold] {test_config.test_type}\n"
            f"[bold]Checks:[/bold] {len(test_config.checks)}",
            title="[bold blue]Validation Result[/bold blue]",
            border_style="green"
        ))
        
    except json.JSONDecodeError as e:
        rich_console.print(Panel(
            f"[bold red]Invalid JSON:[/bold red] {e}",
            border_style="red"
        ))
        sys.exit(ExitCode.JSON_ERROR)
    except Exception as e:
        rich_console.print(Panel(
            f"[bold red]Validation Error:[/bold red] {e}",
            border_style="red"
        ))
        sys.exit(ExitCode.JSON_ERROR)


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Name of the project to initialize"),
    output_dir: Path = typer.Option(
        Path("."),
        "--output",
        "-o",
        help="Output directory for the project",
    )
):
    """Initialize a new test project with templates."""
    project_path = output_dir / project_name
    
    if project_path.exists():
        rich_console.print(f"[red]Error:[/red] Directory {project_path} already exists")
        sys.exit(1)
    
    try:
        project_path.mkdir(parents=True)
        (project_path / "solutions").mkdir()
        (project_path / "test_cases").mkdir()
        
        sample_solution = '''def hello_world():
    """Sample function for testing."""
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
'''
        (project_path / "solutions" / "sample_solution.py").write_text(sample_solution)
        
        sample_test_case = '''{
    "test_id": 1,
    "test_name": "Sample Test",
    "description": "A simple test to verify hello_world function",
    "test_type": "py_general",
    "checks": [
        {
            "check_id": 1,
            "name_for_output": "Test hello_world function",
            "reason_for_output": "Function should return 'Hello, World!'",
            "explain_for_error": "Make sure your hello_world function returns the exact string 'Hello, World!'",
            "spec": {
                "perform": {
                    "action": "call_function",
                    "target": "hello_world"
                },
                "expect": {
                    "return_value": {
                        "assertion": "equals",
                        "value": "Hello, World!"
                    }
                }
            }
        }
    ]
}'''
        (project_path / "test_cases" / "sample_test.json").write_text(sample_test_case)
        
        readme_content = f'''# {project_name}

This is a code-tester project initialized with sample files.

## Structure

- `solutions/` - Put your Python solution files here
- `test_cases/` - Put your JSON test case files here

## Usage

Run tests with:
```bash
code-tester run solutions/sample_solution.py test_cases/sample_test.json
```

Validate test cases with:
```bash
code-tester validate test_cases/sample_test.json
```
'''
        (project_path / "README.md").write_text(readme_content)
        
        rich_console.print(Panel(
            f"[bold green]✅ Project initialized![/bold green]\n"
            f"[bold]Location:[/bold] {project_path}\n"
            f"[bold]Files created:[/bold]\n"
            f"  • solutions/sample_solution.py\n"
            f"  • test_cases/sample_test.json\n"
            f"  • README.md",
            title=f"[bold blue]{project_name}[/bold blue]",
            border_style="green"
        ))
        
        rich_console.print(f"\n[blue]Next steps:[/blue]")
        rich_console.print(f"  cd {project_name}")
        rich_console.print(f"  code-tester run solutions/sample_solution.py test_cases/sample_test.json")
        
    except Exception as e:
        rich_console.print(Panel(
            f"[bold red]Error creating project:[/bold red] {e}",
            border_style="red"
        ))
        sys.exit(1)