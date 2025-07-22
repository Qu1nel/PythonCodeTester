# Legacy import for backward compatibility
# New code should import from src.code_tester.cli directly

from .cli import run_from_cli

__all__ = ["run_from_cli"]