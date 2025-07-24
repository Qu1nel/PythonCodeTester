"""Main tester class for executing test cases."""

import json
from pathlib import Path

from ..config import AppConfig, TestCaseConfig
from ..core import DependencyContainer, PluginManager, PluginRegistry
from .environment import ExecutionEnvironment
from .context import ExecutionContext
from .check_handler import CheckHandler, CheckResult
from ..utils.exceptions import CodeTesterError, TestCaseParsingError
from ..logging import LogLevel, Console, set_test_case, set_check_id, log_initialization
from ..utils import create_dataclass_from_dict


class DynamicTester:
    """Main class for executing dynamic test cases."""
    
    @log_initialization(level=LogLevel.DEBUG)
    def __init__(self, config: AppConfig, console: Console):
        """Initialize the dynamic tester.
        
        Args:
            config: Application configuration
            console: Console instance for output
        """
        self._config = config
        self._console = console
        self._container = DependencyContainer()
        self._plugin_manager = PluginManager(self._container)
        self._environment: ExecutionEnvironment | None = None
        self._test_case_config: TestCaseConfig | None = None
        self._context: ExecutionContext | None = None
        self._check_handler: CheckHandler | None = None
        self._failed_checks: list[CheckResult] = []
        
        self._initialize_plugins()
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize core components."""
        self._context = ExecutionContext()
        self._check_handler = CheckHandler(self._console)

    @property
    def failed_checks_ids(self) -> list[int]:
        """Get list of failed check IDs."""
        return [check.check_id for check in self._failed_checks]

    @property
    def test_case_config(self) -> TestCaseConfig | None:
        """Get the loaded test case configuration."""
        return self._test_case_config

    def _initialize_plugins(self) -> None:
        """Initialize the plugin system."""
        self._console.print("Initializing plugins with new architecture...", level=LogLevel.DEBUG)
        
        registry = PluginRegistry()
        providers = registry.get_all_providers()
        
        for provider in providers:
            self._plugin_manager.register_plugin(provider)
        
        self._plugin_manager.load_all_plugins()
        
        self._console.print(f"Loaded {len(providers)} plugin providers", level=LogLevel.DEBUG)

    def _load_and_parse_test_case(self) -> None:
        """Load and parse test case configuration from JSON file."""
        self._console.print(f"Loading test case from: {self._config.test_case_path}", level=LogLevel.DEBUG)
        try:
            raw_data = json.loads(self._config.test_case_path.read_text("utf-8"))
            self._test_case_config = create_dataclass_from_dict(TestCaseConfig, raw_data)
        except json.JSONDecodeError as e:
            raise TestCaseParsingError(f"Invalid JSON: {e}", path=self._config.test_case_path) from e
        except (TypeError, KeyError) as e:
            raise TestCaseParsingError(f"Malformed structure: {e}", path=self._config.test_case_path) from e

    def _setup_environment(self) -> None:
        """Setup the execution environment."""
        self._console.print("Preparing execution environment...", level=LogLevel.DEBUG)
        self._environment = ExecutionEnvironment(self._config.solution_path, self._console)

    def _execute_setup_actions(self) -> bool:
        """Execute setup actions before running checks.
        
        Returns:
            True if all setup actions succeeded, False otherwise
        """
        if not self._test_case_config or not self._test_case_config.setup_actions:
            return True
        
        self._console.print(f"Executing {len(self._test_case_config.setup_actions)} setup actions...", level=LogLevel.INFO)
        
        for i, setup_action in enumerate(self._test_case_config.setup_actions):
            self._console.print(f"Running setup action {i+1}: {setup_action.action}", level=LogLevel.DEBUG)
            
            try:
                from ..config import PerformConfig
                perform_config = PerformConfig(
                    action=setup_action.action,
                    target=setup_action.target,
                    params=setup_action.params
                )
                
                result = self._execute_single_action(perform_config)
                
                if result.exception:
                    self._console.print(f"Setup action {i+1} failed: {result.exception}", level=LogLevel.ERROR)
                    return False
                
                self._console.print(f"Setup action {i+1} completed successfully", level=LogLevel.DEBUG)
                
            except Exception as e:
                self._console.print(f"Setup action {i+1} failed with error: {e}", level=LogLevel.ERROR)
                return False
        return True
    
    def _execute_single_action(self, perform_config) -> 'ActionResult':
        """Execute a single action and return the result.
        
        Args:
            perform_config: Configuration for the action to perform
            
        Returns:
            ActionResult with the execution result
        """
        if not self._check_handler or not self._environment or not self._context:
            raise RuntimeError("Components not properly initialized")
        
        return self._check_handler._execute_action(perform_config, self._environment, self._context)
    
    def _execute_teardown_actions(self) -> None:
        """Execute teardown actions after running checks.
        
        Teardown actions are executed even if they fail - errors are logged as warnings.
        """
        if not self._test_case_config or not self._test_case_config.teardown_actions:
            return
        
        self._console.print(f"Executing {len(self._test_case_config.teardown_actions)} teardown actions...", level=LogLevel.INFO)
        
        for i, teardown_action in enumerate(self._test_case_config.teardown_actions):
            self._console.print(f"Running teardown action {i+1}: {teardown_action.action}", level=LogLevel.DEBUG)
            
            try:
                from ..config import PerformConfig
                perform_config = PerformConfig(
                    action=teardown_action.action,
                    target=teardown_action.target,
                    params=teardown_action.params
                )
                
                result = self._execute_single_action(perform_config)
                
                if result.exception:
                    self._console.print(f"Teardown action {i+1} failed: {result.exception}", level=LogLevel.WARNING)
                else:
                    self._console.print(f"Teardown action {i+1} completed successfully", level=LogLevel.DEBUG)
                
            except Exception as e:
                self._console.print(f"Teardown action {i+1} failed with error: {e}", level=LogLevel.WARNING)

    def _execute_checks(self) -> None:
        """Execute all checks in the test case."""
        if not self._test_case_config or not self._environment or not self._check_handler or not self._context:
            raise RuntimeError("Components not properly initialized")
        
        set_test_case(self._test_case_config.test_name)
        
        self._console.print(f"Executing {len(self._test_case_config.checks)} checks...", level=LogLevel.INFO)
        
        for check_config in self._test_case_config.checks:
            self._console.print(f"Running check {check_config.check_id}: {check_config.name_for_output}", level=LogLevel.DEBUG)
            
            result = self._check_handler.execute_check(check_config, self._environment, self._context)
            
            if not result.passed:
                self._failed_checks.append(result)
                self._console.print(f"Check {check_config.check_id} failed", level=LogLevel.DEBUG)
                
                if self._config.exit_on_first_error:
                    self._console.print("Stopping execution due to exit_on_first_error flag", level=LogLevel.INFO)
                    break
            else:
                self._console.print(f"Check {check_config.check_id} passed", level=LogLevel.DEBUG)

    def _report_errors(self) -> None:
        """Report failed checks to the user."""
        max_errors = self._config.max_messages
        num_errors = len(self._failed_checks)

        if num_errors == 0:
            return

        errors_to_show = self._failed_checks
        if 0 < max_errors < num_errors:
            errors_to_show = self._failed_checks[:max_errors]

        for check_result in errors_to_show:
            error_message = check_result.error_message or "Check failed"
            self._console.print(error_message, level=LogLevel.WARNING, show_user=True)

        if 0 < max_errors < num_errors:
            remaining_count = num_errors - max_errors
            self._console.print(
                f"... ({remaining_count} more error{'s' if remaining_count > 1 else ''} found)",
                level=LogLevel.WARNING,
                show_user=True,
            )

    def run(self) -> bool:
        """Run the test case.
        
        Returns:
            True if all tests passed, False otherwise
        """
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
        
        try:
            # Execute setup actions first
            if not self._execute_setup_actions():
                self._console.print("Setup actions failed, aborting test execution", level=LogLevel.ERROR, show_user=True)
                return False
            
            # Execute the main checks
            self._execute_checks()
            self._report_errors()
            
            # Return True if no checks failed
            return len(self._failed_checks) == 0
            
        except Exception as e:
            self._console.print(f"Error during test execution: {e}", level=LogLevel.CRITICAL, show_user=True)
            return False
        finally:
            # Always execute teardown actions, even if tests failed
            self._execute_teardown_actions()