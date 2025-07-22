import sys
from typing import Optional

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.text import Text

from .config import LogLevel
from .logger import Logger


class Console:
    def __init__(
        self, 
        logger: Logger,
        is_quiet: bool = False,
        show_verdict: bool = True,
        use_rich: bool = True
    ):
        self.logger = logger
        self.is_quiet = is_quiet
        self.show_verdict = show_verdict
        self.use_rich = use_rich
        
        if use_rich:
            self.rich_console = RichConsole(file=sys.stdout, force_terminal=True)
        else:
            self.rich_console = None
    
    def should_print_to_user(self, is_verdict: bool, show_user: bool) -> bool:
        if self.is_quiet:
            return False
        
        if is_verdict:
            return self.show_verdict
        
        return show_user
    
    def print(
        self,
        message: str,
        *,
        level: LogLevel = LogLevel.INFO,
        is_verdict: bool = False,
        show_user: bool = False,
        **kwargs
    ) -> None:
        # Always log to logger
        log_method = getattr(self.logger, level.lower())
        log_method(message, **kwargs)
        
        # Print to user if needed
        if self.should_print_to_user(is_verdict, show_user):
            self._print_to_user(message, level, is_verdict)
    
    def _print_to_user(self, message: str, level: LogLevel, is_verdict: bool) -> None:
        if not self.use_rich or self.rich_console is None:
            print(message, file=sys.stdout)
            return
        
        if is_verdict:
            self._print_verdict(message, level)
        else:
            self._print_regular(message, level)
    
    def _print_verdict(self, message: str, level: LogLevel) -> None:
        level_styles = {
            LogLevel.INFO: "green",
            LogLevel.SUCCESS: "green", 
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "bold red"
        }
        
        style = level_styles.get(level, "white")
        
        if "✅" in message or "passed" in message.lower():
            panel = Panel(
                Text(message, style="green"),
                title="[green]Test Result[/green]",
                border_style="green"
            )
        elif "❌" in message or "failed" in message.lower():
            panel = Panel(
                Text(message, style="red"),
                title="[red]Test Result[/red]", 
                border_style="red"
            )
        else:
            panel = Panel(
                Text(message, style=style),
                title=f"[{style}]Result[/{style}]",
                border_style=style
            )
        
        self.rich_console.print(panel)
    
    def _print_regular(self, message: str, level: LogLevel) -> None:
        level_styles = {
            LogLevel.TRACE: "dim white",
            LogLevel.DEBUG: "cyan",
            LogLevel.INFO: "blue",
            LogLevel.SUCCESS: "green",
            LogLevel.WARNING: "yellow", 
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "bold red"
        }
        
        style = level_styles.get(level, "white")
        self.rich_console.print(message, style=style)
    
    def print_header(self, title: str) -> None:
        if self.use_rich and self.rich_console:
            self.rich_console.rule(f"[bold blue]{title}[/bold blue]")
        else:
            print(f"\n{'='*50}")
            print(f" {title}")
            print(f"{'='*50}")
    
    def print_progress(self, current: int, total: int, description: str = "") -> None:
        if self.use_rich and self.rich_console:
            percentage = (current / total) * 100 if total > 0 else 0
            progress_text = f"[{current}/{total}] {percentage:.1f}% {description}"
            self.rich_console.print(progress_text, style="cyan")
        else:
            print(f"[{current}/{total}] {description}")
    
    def print_error_details(self, error: Exception, context: Optional[dict] = None) -> None:
        if self.use_rich and self.rich_console:
            error_panel = Panel(
                f"[red]{error.__class__.__name__}[/red]: {str(error)}",
                title="[red]Error Details[/red]",
                border_style="red"
            )
            self.rich_console.print(error_panel)
            
            if context:
                context_text = "\n".join(f"{k}: {v}" for k, v in context.items())
                context_panel = Panel(
                    context_text,
                    title="[yellow]Context[/yellow]",
                    border_style="yellow"
                )
                self.rich_console.print(context_panel)
        else:
            print(f"ERROR: {error.__class__.__name__}: {str(error)}")
            if context:
                print("Context:")
                for k, v in context.items():
                    print(f"  {k}: {v}")