import importlib
import json
import pkgutil
from dataclasses import asdict
from pathlib import Path

from . import LogLevel
from .components.factories import CheckHandlerFactory
from .config import AppConfig, CheckConfig, TestCaseConfig
from .environment import ExecutionEnvironment
from .exceptions import CodeTesterError, TestCaseParsingError
from .output import Console, log_initialization
from .utils import create_dataclass_from_dict


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


class DynamicTester:
    @log_initialization(level=LogLevel.DEBUG)
    def __init__(self, config: AppConfig, console: Console):
        initialize_plugins(console)
        self._config = config
        self._console = console
        self._check_handler_factory = CheckHandlerFactory(self._console)
        self._environment: ExecutionEnvironment | None = None
        self._test_case_config: TestCaseConfig | None = None
        self._failed_checks: list[CheckConfig] = []
        self._config = config
        self._console = console

    @property
    def failed_checks_ids(self) -> list[int]:
        return [check.check_id for check in self._failed_checks]

    @property
    def test_case_config(self) -> TestCaseConfig | None:
        return self._test_case_config

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
        # TODO: Реализовать setup_actions

    def _report_errors(self) -> None:
        max_errors = self._config.max_messages
        num_errors = len(self._failed_checks)

        if num_errors == 0:
            return

        errors_to_show = self._failed_checks
        if 0 < max_errors < num_errors:
            errors_to_show = self._failed_checks[:max_errors]

        for check in errors_to_show:
            # TODO: Выводим reason_for_output, так как он содержит {плейсхолдеры} которые мы в будущем научимся заполнять.
            self._console.print(check.reason_for_output, level=LogLevel.WARNING, show_user=True)

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

        for check_config in self._test_case_config.checks:
            try:
                handler = self._check_handler_factory.create(asdict(check_config))

                is_passed = handler.execute(self._environment)

                if not is_passed:
                    self._failed_checks.append(check_config)
                    if check_config.is_critical or self._config.exit_on_first_error:
                        break

            except CodeTesterError as e:
                self._console.print(f"ERROR in check {check_config.check_id}: {e}", level="ERROR")
                self._failed_checks.append(check_config)
                break
            except Exception as e:
                self._console.print(
                    f"CRITICAL ERROR during check {check_config.check_id}: {e}", level="CRITICAL", exc_info=True
                )
                self._failed_checks.append(check_config)
                break

        self._report_errors()
        # TODO: Реализовать teardown_actions
        return not self._failed_checks
