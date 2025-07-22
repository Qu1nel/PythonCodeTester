import json
from pathlib import Path

from .config import AppConfig, TestCaseConfig
from .core import DependencyContainer, PluginManager, PluginRegistry
from .environment import ExecutionEnvironment
from .exceptions import CodeTesterError, TestCaseParsingError
from .logging import LogLevel, Console, set_test_case, set_check_id, log_initialization
from .utils import create_dataclass_from_dict


class DynamicTester:
    @log_initialization(level=LogLevel.DEBUG)
    def __init__(self, config: AppConfig, console: Console):
        self._config = config
        self._console = console
        self._container = DependencyContainer()
        self._plugin_manager = PluginManager(self._container)
        self._environment: ExecutionEnvironment | None = None
        self._test_case_config: TestCaseConfig | None = None
        self._failed_checks: list[dict] = []
        
        self._initialize_plugins()

    @property
    def failed_checks_ids(self) -> list[int]:
        return [check.get("check_id", 0) for check in self._failed_checks]

    @property
    def test_case_config(self) -> TestCaseConfig | None:
        return self._test_case_config

    def _initialize_plugins(self) -> None:
        self._console.print("Initializing plugins with new architecture...", level=LogLevel.DEBUG)
        
        registry = PluginRegistry()
        providers = registry.get_all_providers()
        
        for provider in providers:
            self._plugin_manager.register_plugin(provider)
        
        self._plugin_manager.load_all_plugins()
        
        self._console.print(f"Loaded {len(providers)} plugin providers", level=LogLevel.DEBUG)

    def _load_and_parse_test_case(self) -> None:
        self._console.print(f"Loading test case from: {self._config.test_case_path}", level=LogLevel.DEBUG)
        try:
            raw_data = json.loads(self._config.test_case_path.read_text("utf-8"))
            self._test_case_config = create_dataclass_from_dict(TestCaseConfig, raw_data)
        except json.JSONDecodeError as e:
            raise TestCaseParsingError(f"Invalid JSON: {e}", path=self._config.test_case_path) from e
        except (TypeError, KeyError) as e:
            raise TestCaseParsingError(f"Malformed structure: {e}", path=self._config.test_case_path) from e

    def _setup_environment(self) -> None:
        self._console.print("Preparing execution environment...", level=LogLevel.DEBUG)
        self._environment = ExecutionEnvironment(self._config.solution_path, self._console)

    def _report_errors(self) -> None:
        max_errors = self._config.max_messages
        num_errors = len(self._failed_checks)

        if num_errors == 0:
            return

        errors_to_show = self._failed_checks
        if 0 < max_errors < num_errors:
            errors_to_show = self._failed_checks[:max_errors]

        for check in errors_to_show:
            reason = check.get("reason_for_output", "Check failed")
            self._console.print(reason, level=LogLevel.WARNING, show_user=True)

        if 0 < max_errors < num_errors:
            remaining_count = num_errors - max_errors
            self._console.print(
                f"... ({remaining_count} more error{'s' if remaining_count > 1 else ''} found)",
                level=LogLevel.WARNING,
                show_user=True,
            )

    def run(self) -> bool:
        try:
            self._load_and_parse_test_case()
            self._setup_environment()
        except (FileNotFoundError, CodeTesterError) as e:
            self._console.print(str(e), level=LogLevel.CRITICAL, show_user=True)
            return False

        if not self._test_case_config or not self._environment:
            self._console.print("Core components were not initialized.", level=LogLevel.CRITICAL)
            return False

        self._console.print("New architecture: Plugin system initialized successfully", level=LogLevel.DEBUG)
        
        return True
