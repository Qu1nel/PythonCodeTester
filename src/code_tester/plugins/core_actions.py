from typing import Any, Dict

from ..core import ComponentMetadata, ComponentProvider, DependencyContainer, plugin_provider
from ..config import PerformConfig
from ..execution import ExecutionEnvironment


class Action:
    def __init__(self, config: PerformConfig):
        self.config = config
    
    def execute(self, environment: ExecutionEnvironment, context: Dict[str, Any]) -> 'ActionResult':
        raise NotImplementedError


class ActionResult:
    def __init__(
        self,
        return_value: Any = None,
        stdout: str | None = None,
        stderr: str | None = None,
        screenshot: Any | None = None,
        http_response: Any | None = None,
        exception: Exception | None = None,
        mock_calls: Dict[str, list] | None = None
    ):
        self.return_value = return_value
        self.stdout = stdout
        self.stderr = stderr
        self.screenshot = screenshot
        self.http_response = http_response
        self.exception = exception
        self.mock_calls = mock_calls


class RunScriptAction(Action):
    def execute(self, environment: ExecutionEnvironment, context: Dict[str, Any]) -> ActionResult:
        stdin_text = self.config.params.get("stdin") if self.config.params else None

        with environment.run_in_isolation(stdin_text) as (module, captured_output):
            if self.config.save_as:
                context[self.config.save_as] = module

        return ActionResult(stdout=captured_output["stdout"], stderr=captured_output["stderr"])


class CallFunctionAction(Action):
    def execute(self, environment: ExecutionEnvironment, context: Dict[str, Any]) -> ActionResult:
        function_name = self.config.target
        args = self.config.params.get("args", []) if self.config.params else []
        kwargs = self.config.params.get("kwargs", {}) if self.config.params else {}
        
        with environment.run_in_isolation() as (module, captured_output):
            if not hasattr(module, function_name):
                raise AttributeError(f"Function '{function_name}' not found in module")
            
            func = getattr(module, function_name)
            try:
                result = func(*args, **kwargs)
                
                if self.config.save_as:
                    context[self.config.save_as] = result
                
                return ActionResult(
                    return_value=result,
                    stdout=captured_output["stdout"],
                    stderr=captured_output["stderr"]
                )
            except Exception as e:
                return ActionResult(
                    exception=e,
                    stdout=captured_output["stdout"],
                    stderr=captured_output["stderr"]
                )


class CreateObjectAction(Action):
    def execute(self, environment: ExecutionEnvironment, context: Dict[str, Any]) -> ActionResult:
        class_name = self.config.target
        args = self.config.params.get("args", []) if self.config.params else []
        kwargs = self.config.params.get("kwargs", {}) if self.config.params else {}
        
        with environment.run_in_isolation() as (module, captured_output):
            if not hasattr(module, class_name):
                raise AttributeError(f"Class '{class_name}' not found in module")
            
            cls = getattr(module, class_name)
            try:
                instance = cls(*args, **kwargs)
                
                if self.config.save_as:
                    context[self.config.save_as] = instance
                
                return ActionResult(
                    return_value=instance,
                    stdout=captured_output["stdout"],
                    stderr=captured_output["stderr"]
                )
            except Exception as e:
                return ActionResult(
                    exception=e,
                    stdout=captured_output["stdout"],
                    stderr=captured_output["stderr"]
                )


class CallMethodAction(Action):
    def execute(self, environment: ExecutionEnvironment, context: Dict[str, Any]) -> ActionResult:
        method_name = self.config.target
        object_ref = self.config.params.get("object_ref") if self.config.params else None
        args = self.config.params.get("args", []) if self.config.params else []
        kwargs = self.config.params.get("kwargs", {}) if self.config.params else {}
        
        if not object_ref or object_ref not in context:
            raise ValueError(f"Object reference '{object_ref}' not found in context")
        
        obj = context[object_ref]
        
        if not hasattr(obj, method_name):
            raise AttributeError(f"Method '{method_name}' not found on object")
        
        method = getattr(obj, method_name)
        try:
            result = method(*args, **kwargs)
            
            if self.config.save_as:
                context[self.config.save_as] = result
            
            return ActionResult(return_value=result)
        except Exception as e:
            return ActionResult(exception=e)


class GetAttributeAction(Action):
    def execute(self, environment: ExecutionEnvironment, context: Dict[str, Any]) -> ActionResult:
        attribute_name = self.config.target
        object_ref = self.config.params.get("object_ref") if self.config.params else None
        
        if not object_ref or object_ref not in context:
            raise ValueError(f"Object reference '{object_ref}' not found in context")
        
        obj = context[object_ref]
        
        if not hasattr(obj, attribute_name):
            raise AttributeError(f"Attribute '{attribute_name}' not found on object")
        
        try:
            result = getattr(obj, attribute_name)
            
            if self.config.save_as:
                context[self.config.save_as] = result
            
            return ActionResult(return_value=result)
        except Exception as e:
            return ActionResult(exception=e)


class ReadFileContentAction(Action):
    def execute(self, environment: ExecutionEnvironment, context: Dict[str, Any]) -> ActionResult:
        file_path = self.config.target
        encoding = self.config.params.get("encoding", "utf-8") if self.config.params else "utf-8"
        
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            
            if self.config.save_as:
                context[self.config.save_as] = content
            
            return ActionResult(return_value=content)
        except Exception as e:
            return ActionResult(exception=e)


@plugin_provider(ComponentMetadata(
    name="core_actions",
    version="1.0.0",
    test_types=["py_general", "api", "flask", "arcade"]
))
class CoreActionsProvider(ComponentProvider):
    def register_components(self, container: DependencyContainer) -> None:
        action_factories = {
            "run_script": RunScriptAction,
            "call_function": CallFunctionAction,
            "create_object": CreateObjectAction,
            "call_method": CallMethodAction,
            "get_attribute": GetAttributeAction,
            "read_file_content": ReadFileContentAction,
        }
        
        for action_name, action_class in action_factories.items():
            container.register_factory(
                f"action_{action_name}",
                lambda cls=action_class: cls
            )