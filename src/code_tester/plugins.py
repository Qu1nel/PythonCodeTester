import importlib
import pkgutil
from pathlib import Path

from .logging import LogLevel, Console


def initialize_plugins(logger: Console):
    logger.print("Initializing and registering framework plugins...", level=LogLevel.DEBUG)

    from . import actions_library, assertions_library

    _discover_plugins(actions_library)
    _discover_plugins(assertions_library)

    from .components.definitions import action_registry, assertion_registry

    logger.print(f"Discovered and registered {len(action_registry.get_all_registry)} Actions.", level=LogLevel.INFO)
    logger.print(
        f"Discovered and registered {len(assertion_registry.get_all_registry)} Assertions.", level=LogLevel.INFO
    )

    logger.print("Framework plugins initialized successfully.", level=LogLevel.DEBUG)


def _discover_plugins(package):
    package_path = Path(package.__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        full_module_path = f"{package.__name__}.{module_name}"
        importlib.import_module(full_module_path)
