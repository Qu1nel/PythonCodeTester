"""Main CLI interface for the code tester."""

from .commands import app


def run_from_cli() -> None:
    """Main CLI entry point."""
    app()