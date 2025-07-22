import sys
from typing import Dict, Any

from loguru import logger
from rich.console import Console
from rich.text import Text


class ConsoleFormatter:
    def __init__(self, colorize: bool = True):
        self.colorize = colorize
        self.console = Console(file=sys.stderr, force_terminal=colorize)
    
    def format(self, record: Dict[str, Any]) -> str:
        if not self.colorize:
            return self._format_plain(record)
        return self._format_rich(record)
    
    def _format_plain(self, record: Dict[str, Any]) -> str:
        return (
            f"{record['time'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | "
            f"{record['level'].name:<8} | "
            f"{record['name']}:{record['function']}:{record['line']} | "
            f"{record['message']}"
        )
    
    def _format_rich(self, record: Dict[str, Any]) -> str:
        level_colors = {
            "TRACE": "dim white",
            "DEBUG": "cyan",
            "INFO": "blue", 
            "SUCCESS": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold red"
        }
        
        level_name = record['level'].name
        level_color = level_colors.get(level_name, "white")
        
        time_text = Text(record['time'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], style="green")
        level_text = Text(f"{level_name:<8}", style=level_color)
        location_text = Text(f"{record['name']}:{record['function']}:{record['line']}", style="cyan")
        message_text = Text(record['message'], style=level_color)
        
        return f"{time_text} | {level_text} | {location_text} | {message_text}"


class FileFormatter:
    def format(self, record: Dict[str, Any]) -> str:
        return (
            f"{record['time'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | "
            f"{record['level'].name:<8} | "
            f"{record['process'].id:>5} | "
            f"{record['thread'].id:>5} | "
            f"{record['name']}:{record['function']}:{record['line']} | "
            f"{record['message']}"
        )


class JsonFormatter:
    def format(self, record: Dict[str, Any]) -> str:
        import json
        
        log_entry = {
            "timestamp": record['time'].isoformat(),
            "level": record['level'].name,
            "logger": record['name'],
            "function": record['function'],
            "line": record['line'],
            "message": record['message'],
            "process_id": record['process'].id,
            "thread_id": record['thread'].id,
        }
        
        if record.get('extra'):
            log_entry.update(record['extra'])
        
        return json.dumps(log_entry, ensure_ascii=False)