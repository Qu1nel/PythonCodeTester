import pytest
from code_tester.utils.placeholder_resolver import PlaceholderResolver


class TestPlaceholderResolver:
    
    def setup_method(self):
        self.resolver = PlaceholderResolver()
    
    def test_resolve_simple_placeholders(self):
        template = "Expected {expected}, got {actual}"
        context = {"expected": 42, "actual": 24}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Expected 42, got 24"
    
    def test_resolve_string_values(self):
        template = "Expected {expected}, got {actual}"
        context = {"expected": "hello", "actual": "world"}
        
        result = self.resolver.resolve(template, context)
        
        assert result == 'Expected "hello", got "world"'
    
    def test_resolve_none_value(self):
        template = "Value is {value}"
        context = {"value": None}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Value is None"
    
    def test_resolve_boolean_values(self):
        template = "Flag is {flag}, other is {other}"
        context = {"flag": True, "other": False}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Flag is True, other is False"
    
    def test_resolve_list_values(self):
        template = "List is {list}"
        context = {"list": [1, 2, 3]}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "List is [1, 2, 3]"
    
    def test_resolve_long_list_values(self):
        template = "Long list is {list}"
        context = {"list": [1, 2, 3, 4, 5, 6, 7, 8]}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Long list is [1, 2, 3, ... (8 items total)]"
    
    def test_resolve_empty_list(self):
        template = "Empty list is {list}"
        context = {"list": []}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Empty list is []"
    
    def test_resolve_tuple_values(self):
        template = "Tuple is {tuple}"
        context = {"tuple": (1, 2, 3)}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Tuple is (1, 2, 3)"
    
    def test_resolve_dict_values(self):
        template = "Dict is {dict}"
        context = {"dict": {"a": 1, "b": 2}}
        
        result = self.resolver.resolve(template, context)
        
        assert result == 'Dict is {"a": 1, "b": 2}'
    
    def test_resolve_large_dict_values(self):
        template = "Large dict is {dict}"
        context = {"dict": {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}}
        
        result = self.resolver.resolve(template, context)
        
        assert result == 'Large dict is {"a": 1, "b": 2, ... (5 items total)}'
    
    def test_resolve_empty_dict(self):
        template = "Empty dict is {dict}"
        context = {"dict": {}}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Empty dict is {}"
    
    def test_resolve_exception_values(self):
        template = "Exception is {error}"
        context = {"error": ValueError("Something went wrong")}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Exception is ValueError: Something went wrong"
    
    def test_resolve_custom_object(self):
        class CustomClass:
            pass
        
        template = "Object is {obj}"
        context = {"obj": CustomClass()}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Object is <CustomClass object>"
    
    def test_resolve_no_placeholders(self):
        template = "No placeholders here"
        context = {"unused": "value"}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "No placeholders here"
    
    def test_resolve_missing_placeholder(self):
        template = "Expected {expected}, got {actual}, missing {missing}"
        context = {"expected": 42, "actual": 24}
        
        result = self.resolver.resolve(template, context)
        
        assert result == "Expected 42, got 24, missing {missing}"
    
    def test_format_value_nested_structures(self):
        nested_list = [{"a": 1}, {"b": [2, 3]}]
        
        result = self.resolver.format_value(nested_list)
        
        assert result == '[{"a": 1}, {"b": [2, 3]}]'
    
    def test_format_value_complex_nested(self):
        complex_data = {
            "numbers": [1, 2, 3, 4, 5, 6],
            "nested": {"inner": True}
        }
        
        result = self.resolver.format_value(complex_data)
        
        assert result == '{"numbers": [1, 2, 3, ... (6 items total)], "nested": {"inner": True}}'