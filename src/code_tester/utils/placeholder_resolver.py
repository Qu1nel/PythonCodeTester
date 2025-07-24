from typing import Any, Dict
import json


class PlaceholderResolver:
    
    def resolve(self, template: str, context: Dict[str, Any]) -> str:
        message = template
        
        for placeholder, value in context.items():
            placeholder_pattern = f"{{{placeholder}}}"
            if placeholder_pattern in message:
                formatted_value = self.format_value(value)
                message = message.replace(placeholder_pattern, formatted_value)
        
        return message
    
    def format_value(self, value: Any) -> str:
        if value is None:
            return "None"
        
        if isinstance(value, str):
            return f'"{value}"'
        
        if isinstance(value, bool):
            return str(value)
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, (list, tuple)):
            return self._format_sequence(value)
        
        if isinstance(value, dict):
            return self._format_dict(value)
        
        if isinstance(value, Exception):
            return f"{type(value).__name__}: {str(value)}"
        
        if hasattr(value, '__class__'):
            return f"<{type(value).__name__} object>"
        
        return str(value)
    
    def _format_sequence(self, seq: Any) -> str:
        if len(seq) == 0:
            return "[]" if isinstance(seq, list) else "()"
        
        if len(seq) <= 5:
            formatted_items = [self.format_value(item) for item in seq]
            bracket_open = "[" if isinstance(seq, list) else "("
            bracket_close = "]" if isinstance(seq, list) else ")"
            return f"{bracket_open}{', '.join(formatted_items)}{bracket_close}"
        else:
            first_items = [self.format_value(item) for item in seq[:3]]
            bracket_open = "[" if isinstance(seq, list) else "("
            bracket_close = "]" if isinstance(seq, list) else ")"
            return f"{bracket_open}{', '.join(first_items)}, ... ({len(seq)} items total){bracket_close}"
    
    def _format_dict(self, d: Dict[str, Any]) -> str:
        if len(d) == 0:
            return "{}"
        
        if len(d) <= 3:
            formatted_items = []
            for key, value in d.items():
                formatted_key = self.format_value(key) if not isinstance(key, str) else f'"{key}"'
                formatted_value = self.format_value(value)
                formatted_items.append(f"{formatted_key}: {formatted_value}")
            return f"{{{', '.join(formatted_items)}}}"
        else:
            first_items = []
            for i, (key, value) in enumerate(d.items()):
                if i >= 2:
                    break
                formatted_key = self.format_value(key) if not isinstance(key, str) else f'"{key}"'
                formatted_value = self.format_value(value)
                first_items.append(f"{formatted_key}: {formatted_value}")
            return f"{{{', '.join(first_items)}, ... ({len(d)} items total)}}"