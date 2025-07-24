from typing import Any, Dict, Type

from ..config import CheckConfig, PerformConfig, ExpectConfig
from ..plugins.core_actions import Action, ActionResult
from ..plugins.core_assertions import Assertion
from ..utils.exceptions import ActionError, AssertionError
from ..utils.placeholder_resolver import PlaceholderResolver
from ..logging import LogLevel, Console, set_check_id
from .environment import ExecutionEnvironment
from .context import ExecutionContext


class CheckResult:
    def __init__(
        self,
        check_id: int,
        passed: bool,
        action_result: ActionResult = None,
        error_message: str = None,
        exception: Exception = None
    ):
        self.check_id = check_id
        self.passed = passed
        self.action_result = action_result
        self.error_message = error_message
        self.exception = exception


class CheckHandler:
    def __init__(self, console: Console):
        self._console = console
        self._action_factories: Dict[str, Type[Action]] = {}
        self._assertion_factories: Dict[str, Type[Assertion]] = {}
        self._placeholder_resolver = PlaceholderResolver()
        
        self._register_default_components()
    
    def _register_default_components(self) -> None:
        from ..plugins.core_actions import (
            RunScriptAction, CallFunctionAction, CreateObjectAction,
            CallMethodAction, GetAttributeAction, ReadFileContentAction
        )
        from ..plugins.core_assertions import (
            EqualsAssertion, ContainsAssertion, IsInRangeAssertion,
            IsCloseToAssertion, IsInstanceOfAssertion, RaisesExceptionAssertion,
            HasLengthAssertion
        )
        
        self._action_factories = {
            "run_script": RunScriptAction,
            "call_function": CallFunctionAction,
            "create_object": CreateObjectAction,
            "call_method": CallMethodAction,
            "get_attribute": GetAttributeAction,
            "read_file_content": ReadFileContentAction,
        }
        
        self._assertion_factories = {
            "equals": EqualsAssertion,
            "contains": ContainsAssertion,
            "is_in_range": IsInRangeAssertion,
            "is_close_to": IsCloseToAssertion,
            "is_instance_of": IsInstanceOfAssertion,
            "raises_exception": RaisesExceptionAssertion,
            "has_length": HasLengthAssertion,
        }
    
    def execute_check(
        self,
        check_config: CheckConfig,
        environment: ExecutionEnvironment,
        context: ExecutionContext
    ) -> CheckResult:
        set_check_id(str(check_config.check_id))
        
        self._console.print(
            f"Executing check {check_config.check_id}: {check_config.name_for_output}",
            level=LogLevel.DEBUG
        )
        
        try:
            action_result = self._execute_action(
                check_config.spec.perform,
                environment,
                context
            )
            
            if action_result.exception:
                if self._should_check_exception(check_config.spec.expect):
                    passed = self._check_expectations(check_config.spec.expect, action_result)
                    return CheckResult(check_config.check_id, passed, action_result)
                else:
                    return CheckResult(
                        check_config.check_id,
                        False,
                        action_result,
                        f"Action failed with exception: {action_result.exception}",
                        action_result.exception
                    )
            
            passed = self._check_expectations(check_config.spec.expect, action_result)
            
            if not passed:
                error_message = self._format_error_message(
                    check_config.reason_for_output,
                    action_result,
                    check_config.spec.expect
                )
            else:
                error_message = None
            
            return CheckResult(check_config.check_id, passed, action_result, error_message)
            
        except Exception as e:
            self._console.print(
                f"Error executing check {check_config.check_id}: {e}",
                level=LogLevel.ERROR
            )
            return CheckResult(
                check_config.check_id,
                False,
                None,
                f"Check execution failed: {e}",
                e
            )
    
    def _execute_action(
        self,
        perform_config: PerformConfig,
        environment: ExecutionEnvironment,
        context: ExecutionContext
    ) -> ActionResult:
        action_name = perform_config.action
        
        if action_name not in self._action_factories:
            raise ActionError(
                f"Unknown action: {action_name}",
                check_id=0,
                action=action_name
            )
        
        action_class = self._action_factories[action_name]
        action = action_class(perform_config)
        
        # Convert ExecutionContext to dict for backward compatibility
        context_dict = context.get_all_objects()
        
        result = action.execute(environment, context_dict)
        
        # Save result if save_as is specified
        if perform_config.save_as and result.return_value is not None:
            context.save_object(perform_config.save_as, result.return_value)
        
        return result
    
    def _check_expectations(self, expectation, action_result: ActionResult) -> bool:
        if expectation.return_value:
            # Special handling for exception assertions
            if expectation.return_value.assertion == "raises_exception":
                if not self._check_assertion(expectation.return_value, action_result.exception):
                    return False
            else:
                if not self._check_assertion(expectation.return_value, action_result.return_value):
                    return False
        
        if expectation.stdout:
            if not self._check_assertion(expectation.stdout, action_result.stdout):
                return False
        
        if expectation.stderr:
            if not self._check_assertion(expectation.stderr, action_result.stderr):
                return False
        
        return True
    
    def _check_assertion(self, expect_config: ExpectConfig, actual_value: Any) -> bool:
        assertion_name = expect_config.assertion
        
        if assertion_name not in self._assertion_factories:
            raise AssertionError(f"Unknown assertion: {assertion_name}")
        
        assertion_class = self._assertion_factories[assertion_name]
        assertion = assertion_class(expect_config)
        
        return assertion.check(actual_value)
    
    def _should_check_exception(self, expectation) -> bool:
        return (expectation.return_value and 
                expectation.return_value.assertion == "raises_exception")
    
    def _format_error_message(
        self,
        template: str,
        action_result: ActionResult,
        expectation
    ) -> str:
        context = {}
        
        if action_result.return_value is not None:
            context["actual"] = action_result.return_value
        
        if expectation.return_value:
            context["expected"] = expectation.return_value.value
        
        if action_result.stdout:
            context["stdout"] = action_result.stdout
        
        if action_result.stderr:
            context["stderr"] = action_result.stderr
        
        if action_result.exception:
            context["exception"] = action_result.exception
        
        return self._placeholder_resolver.resolve(template, context)