import logging
from typing import Any

from ..config import CheckConfig, ExpectConfig, PerformConfig
from ..exceptions import TestCaseParsingError
from ..output import Console
from ..utils import create_dataclass_from_dict
from .definitions import Action, Assertion, CheckHandler, action_registry, assertion_registry
from .handlers import DefaultCheckHandler, ExpectationHandler


class ActionFactory:
    @staticmethod
    def create(config: PerformConfig) -> Action:
        handler_class = action_registry.get(config.action)
        if handler_class:
            return handler_class(config)
        raise TestCaseParsingError(f"Action type '{config.action}' not implemented.")


class AssertionFactory:
    @staticmethod
    def create(config: ExpectConfig) -> Assertion:
        logging.getLogger().error(f"{config = }, {type(config) = }")
        logging.getLogger().error(f"{action_registry.get_all_registry = }, {assertion_registry.get_all_registry = }")
        handler_class = assertion_registry.get(config.assertion)
        logging.getLogger().error(f"{handler_class = }, {type(handler_class) = }")
        if handler_class:
            return handler_class(config)
        raise TestCaseParsingError(f"Assertion type '{config.assertion}' not implemented.")


class CheckHandlerFactory:
    def __init__(self, console: Console):
        self.console = console
        self.action_factory = ActionFactory()
        self.assertion_factory = AssertionFactory()

    def create(self, check_config_dict: dict[str, Any]) -> CheckHandler:
        config = create_dataclass_from_dict(CheckConfig, check_config_dict)
        action = self.action_factory.create(config.spec.perform)

        expectation_handler = ExpectationHandler(config.spec.expect, self.console, self.assertion_factory)

        return DefaultCheckHandler(config, action, expectation_handler, self.console)
