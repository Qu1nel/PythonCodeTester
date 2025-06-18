from .components.definitions import Action, Assertion
from .components.factories import ActionFactory, AssertionFactory
from .config import AppConfig, CheckConfig, TestCaseConfig
from .output import Console, LogLevel


class DynamicTester:
    """Orchestrates the dynamic testing process for a single test case."""

    def __init__(self, config: AppConfig, console: Console):
        self._config = config
        self._console = console
        self._test_case_config: TestCaseConfig | None = None
        # TODO: Загрузка и парсинг test_case.json

    def _setup_environment(self) -> None:
        """Executes setup_actions defined in the test case."""
        # TODO: Реализовать логику для self._test_case_config.setup_actions
        self._console.print("Setting up test environment...", level=LogLevel.DEBUG)

    def _teardown_environment(self) -> None:
        """Executes teardown_actions if they were defined."""
        # TODO: Реализовать teardown
        self._console.print("Tearing down test environment.", level=LogLevel.DEBUG)

    def _run_check(self, check_config: CheckConfig) -> bool:
        """Runs a single check from the test case."""
        self._console.print(f"Running check: {check_config.check_id} - {check_config.name_for_output}",
                            level=LogLevel.INFO)

        # 1. Создание компонентов через фабрики (пока заглушки)
        action_factory = ActionFactory(check_config.spec.perform)
        action: Action = action_factory.create()

        # 2. Выполнение действия
        action_result = action.execute()

        # 3. Проверка всех ожиданий (expectations)
        # TODO: Итерироваться по `check_config.spec.expect` и для каждого создавать
        # и выполнять соответствующий Assertion.

        is_passed = True  # Заглушка
        return is_passed

    def run(self) -> bool:
        """Runs the entire test case."""
        # TODO: Загрузить self._test_case_config из файла

        self._setup_environment()

        all_passed = True
        for check in self._test_case_config.checks:
            if not self._run_check(check):
                all_passed = False
                if check.is_critical or self._config.stop_on_first_fail:
                    self._console.print("Critical check failed. Halting.", level=LogLevel.WARNING)
                    break

        self._teardown_environment()
        return all_passed