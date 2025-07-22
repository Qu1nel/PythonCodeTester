# Legacy import for backward compatibility
# New code should import from src.code_tester.execution directly

from .execution import DynamicTester

__all__ = ["DynamicTester"]