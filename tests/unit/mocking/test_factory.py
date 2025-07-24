import pytest
from unittest.mock import Mock

from code_tester.config.mocks import MockConfig
from code_tester.mocking.factory import MockFactory
from code_tester.utils.exceptions import MockError


class TestMockFactory:
    
    @pytest.fixture
    def factory(self):
        return MockFactory()
    
    def test_create_return_value_mock(self, factory):
        config = MockConfig(
            target_path="requests.get",
            behavior={"return_value": 42}
        )
        
        mock = factory.create_mock(config)
        
        assert isinstance(mock, Mock)
        assert mock.return_value == 42
        assert mock() == 42
    
    def test_create_return_object_mock_with_attributes(self, factory):
        config = MockConfig(
            target_path="requests.get",
            behavior={
                "return_object": {
                    "attributes": {
                        "status_code": 200,
                        "text": "OK"
                    }
                }
            }
        )
        
        mock = factory.create_mock(config)
        
        assert mock.status_code == 200
        assert mock.text == "OK"
    
    def test_create_return_object_mock_with_methods(self, factory):
        config = MockConfig(
            target_path="requests.get",
            behavior={
                "return_object": {
                    "methods": {
                        "json": {"return_value": {"id": 1, "name": "test"}},
                        "raise_for_status": {"return_value": None}
                    }
                }
            }
        )
        
        mock = factory.create_mock(config)
        
        assert mock.json() == {"id": 1, "name": "test"}
        assert mock.raise_for_status() is None
    
    def test_create_return_object_mock_with_attributes_and_methods(self, factory):
        config = MockConfig(
            target_path="requests.get",
            behavior={
                "return_object": {
                    "attributes": {"status_code": 200},
                    "methods": {"json": {"return_value": {"data": "test"}}}
                }
            }
        )
        
        mock = factory.create_mock(config)
        
        assert mock.status_code == 200
        assert mock.json() == {"data": "test"}
    
    def test_create_side_effect_mock_with_exception(self, factory):
        config = MockConfig(
            target_path="requests.get",
            behavior={
                "side_effect": {
                    "raises_exception": {
                        "type": "ConnectionError",
                        "message": "Connection failed"
                    }
                }
            }
        )
        
        mock = factory.create_mock(config)
        
        with pytest.raises(ConnectionError, match="Connection failed"):
            mock()
    
    def test_create_side_effect_mock_with_sequence(self, factory):
        config = MockConfig(
            target_path="requests.get",
            behavior={
                "side_effect": {
                    "sequence": [
                        {"return_value": "first"},
                        {"return_value": "second"},
                        {"raises_exception": {"type": "ValueError", "message": "Third call fails"}}
                    ]
                }
            }
        )
        
        mock = factory.create_mock(config)
        
        assert mock() == "first"
        assert mock() == "second"
        with pytest.raises(ValueError, match="Third call fails"):
            mock()
    
    def test_create_side_effect_mock_different_exception_types(self, factory):
        test_cases = [
            ("ConnectionError", ConnectionError),
            ("ValueError", ValueError),
            ("RuntimeError", RuntimeError),
            ("UnknownError", Exception)
        ]
        
        for exception_type, expected_class in test_cases:
            config = MockConfig(
                target_path="test.func",
                behavior={
                    "side_effect": {
                        "raises_exception": {
                            "type": exception_type,
                            "message": f"Test {exception_type}"
                        }
                    }
                }
            )
            
            mock = factory.create_mock(config)
            
            with pytest.raises(expected_class, match=f"Test {exception_type}"):
                mock()
    
    def test_create_mock_multiple_behavior_keys_raises_error(self, factory):
        config = MockConfig(
            target_path="test.func",
            behavior={"return_value": "valid", "return_object": {"attributes": {}}}
        )
        
        with pytest.raises(MockError, match="Behavior must contain exactly one of"):
            factory.create_mock(config)
    
    def test_create_side_effect_unsupported_config_raises_error(self, factory):
        config = MockConfig(
            target_path="test.func",
            behavior={
                "side_effect": {"unsupported_key": "value"}
            }
        )
        
        with pytest.raises(MockError, match="Unsupported side_effect configuration"):
            factory.create_mock(config)
    
    def test_create_return_value_mock_direct(self, factory):
        mock = factory.create_return_value_mock("test_value")
        
        assert isinstance(mock, Mock)
        assert mock.return_value == "test_value"
        assert mock() == "test_value"
    
    def test_create_return_object_mock_direct(self, factory):
        spec = {
            "attributes": {"attr1": "value1"},
            "methods": {"method1": {"return_value": "result1"}}
        }
        
        mock = factory.create_return_object_mock(spec)
        
        assert mock.attr1 == "value1"
        assert mock.method1() == "result1"
    
    def test_create_side_effect_mock_direct(self, factory):
        config = {"raises_exception": {"type": "ValueError", "message": "Direct test"}}
        
        mock = factory.create_side_effect_mock(config)
        
        with pytest.raises(ValueError, match="Direct test"):
            mock()