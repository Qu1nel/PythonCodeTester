import pytest
from unittest.mock import Mock, patch

from code_tester.config.mocks import MockConfig
from code_tester.mocking.manager import MockManager
from code_tester.utils.exceptions import MockError


class TestMockManager:
    
    @pytest.fixture
    def manager(self):
        return MockManager()
    
    @pytest.fixture
    def sample_mock_configs(self):
        return [
            MockConfig(
                target_path="requests.get",
                behavior={"return_value": "mocked_response"},
                save_as="get_mock"
            ),
            MockConfig(
                target_path="os.path.exists",
                behavior={"return_value": True},
                save_as="exists_mock"
            )
        ]
    
    def test_setup_mocks_success(self, manager, sample_mock_configs):
        active_mocks = manager.setup_mocks(sample_mock_configs)
        
        assert len(active_mocks) == 2
        assert "get_mock" in active_mocks
        assert "exists_mock" in active_mocks
        assert isinstance(active_mocks["get_mock"], Mock)
        assert isinstance(active_mocks["exists_mock"], Mock)
        
        manager.teardown_mocks()
    
    def test_setup_mocks_without_save_as(self, manager):
        configs = [
            MockConfig(
                target_path="requests.get",
                behavior={"return_value": "response"}
            )
        ]
        
        active_mocks = manager.setup_mocks(configs)
        
        assert len(active_mocks) == 0
        assert len(manager._patches) == 1
        
        manager.teardown_mocks()
    
    def test_teardown_mocks(self, manager, sample_mock_configs):
        manager.setup_mocks(sample_mock_configs)
        
        assert len(manager._active_mocks) == 2
        assert len(manager._patches) == 2
        
        manager.teardown_mocks()
        
        assert len(manager._active_mocks) == 0
        assert len(manager._patches) == 0
    
    def test_get_mock_success(self, manager, sample_mock_configs):
        manager.setup_mocks(sample_mock_configs)
        
        mock = manager.get_mock("get_mock")
        assert isinstance(mock, Mock)
        
        manager.teardown_mocks()
    
    def test_get_mock_not_found_raises_error(self, manager):
        with pytest.raises(MockError, match="Mock 'nonexistent' not found"):
            manager.get_mock("nonexistent")
    
    def test_get_mock_calls(self, manager, sample_mock_configs):
        manager.setup_mocks(sample_mock_configs)
        
        mock = manager.get_mock("get_mock")
        mock("arg1", kwarg1="value1")
        mock("arg2", kwarg2="value2")
        
        calls = manager.get_mock_calls("get_mock")
        assert len(calls) == 2
        
        manager.teardown_mocks()
    
    def test_get_mock_call_count(self, manager, sample_mock_configs):
        manager.setup_mocks(sample_mock_configs)
        
        mock = manager.get_mock("get_mock")
        mock()
        mock()
        mock()
        
        count = manager.get_mock_call_count("get_mock")
        assert count == 3
        
        manager.teardown_mocks()
    
    def test_was_mock_called(self, manager, sample_mock_configs):
        manager.setup_mocks(sample_mock_configs)
        
        assert not manager.was_mock_called("get_mock")
        
        mock = manager.get_mock("get_mock")
        mock()
        
        assert manager.was_mock_called("get_mock")
        
        manager.teardown_mocks()
    
    def test_reset_mock(self, manager, sample_mock_configs):
        manager.setup_mocks(sample_mock_configs)
        
        mock = manager.get_mock("get_mock")
        mock()
        mock()
        
        assert manager.get_mock_call_count("get_mock") == 2
        
        manager.reset_mock("get_mock")
        
        assert manager.get_mock_call_count("get_mock") == 0
        assert not manager.was_mock_called("get_mock")
        
        manager.teardown_mocks()
    
    def test_reset_all_mocks(self, manager, sample_mock_configs):
        manager.setup_mocks(sample_mock_configs)
        
        get_mock = manager.get_mock("get_mock")
        exists_mock = manager.get_mock("exists_mock")
        
        get_mock()
        exists_mock()
        
        assert manager.get_mock_call_count("get_mock") == 1
        assert manager.get_mock_call_count("exists_mock") == 1
        
        manager.reset_all_mocks()
        
        assert manager.get_mock_call_count("get_mock") == 0
        assert manager.get_mock_call_count("exists_mock") == 0
        
        manager.teardown_mocks()
    
    def test_setup_mocks_failure_cleanup(self, manager):
        configs = [
            MockConfig(
                target_path="valid.module.function",
                behavior={"return_value": "ok"},
                save_as="valid_mock"
            ),
            MockConfig(
                target_path="invalid..path",
                behavior={"return_value": "fail"}
            )
        ]
        
        with pytest.raises(MockError):
            manager.setup_mocks(configs)
        
        assert len(manager._active_mocks) == 0
        assert len(manager._patches) == 0
    
    def test_teardown_mocks_handles_runtime_error(self, manager):
        manager._patches = [Mock()]
        manager._patches[0].stop.side_effect = RuntimeError("Already stopped")
        
        manager.teardown_mocks()
        
        assert len(manager._patches) == 0
    
    def test_multiple_setup_teardown_cycles(self, manager, sample_mock_configs):
        for _ in range(3):
            active_mocks = manager.setup_mocks(sample_mock_configs)
            assert len(active_mocks) == 2
            
            manager.teardown_mocks()
            assert len(manager._active_mocks) == 0