import importlib
from typing import Any, Dict, List
from unittest.mock import Mock, patch

from code_tester.config.mocks import MockConfig
from code_tester.mocking.factory import MockFactory
from code_tester.utils.exceptions import MockError


class MockManager:
    
    def __init__(self):
        self._factory = MockFactory()
        self._active_mocks: Dict[str, Mock] = {}
        self._patches: List[Any] = []
    
    def setup_mocks(self, mock_configs: List[MockConfig]) -> Dict[str, Mock]:
        self.teardown_mocks()
        
        for config in mock_configs:
            try:
                mock_obj = self._factory.create_mock(config)
                
                patcher = patch(config.target_path, mock_obj)
                patcher.start()
                self._patches.append(patcher)
                
                if config.save_as:
                    self._active_mocks[config.save_as] = mock_obj
                
            except Exception as e:
                self.teardown_mocks()
                raise MockError(f"Failed to setup mock for {config.target_path}: {e}")
        
        return self._active_mocks.copy()
    
    def teardown_mocks(self) -> None:
        for patcher in self._patches:
            try:
                patcher.stop()
            except RuntimeError:
                pass
        
        self._patches.clear()
        self._active_mocks.clear()
    
    def get_mock(self, name: str) -> Mock:
        if name not in self._active_mocks:
            raise MockError(f"Mock '{name}' not found. Available mocks: {list(self._active_mocks.keys())}")
        return self._active_mocks[name]
    
    def get_mock_calls(self, name: str) -> List[Any]:
        mock = self.get_mock(name)
        return mock.call_args_list
    
    def get_mock_call_count(self, name: str) -> int:
        mock = self.get_mock(name)
        return mock.call_count
    
    def was_mock_called(self, name: str) -> bool:
        mock = self.get_mock(name)
        return mock.called
    
    def reset_mock(self, name: str) -> None:
        mock = self.get_mock(name)
        mock.reset_mock()
    
    def reset_all_mocks(self) -> None:
        for mock in self._active_mocks.values():
            mock.reset_mock()