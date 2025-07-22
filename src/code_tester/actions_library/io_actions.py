from typing import Any

from ..components.definitions import Action, ActionResult, action_registry
from ..config import PerformConfig
from ..environment import ExecutionEnvironment


@action_registry.register("run_script")
class RunScriptAction(Action):
    def __init__(self, config: PerformConfig):
        self.config = config

    def execute(self, environment: ExecutionEnvironment, context: dict[str, Any]) -> ActionResult:
        stdin_text = self.config.params.get("stdin") if self.config.params else None

        with environment.run_in_isolation(stdin_text) as (module, captured_output):
            pass

        return ActionResult(stdout=captured_output["stdout"], stderr=captured_output["stderr"])
