from datetime import date

from rich.console import Console


class Renderer:
    def __init__(self, console: Console | None = None, test_mode: bool = False) -> None:
        self.console = console or Console()
        self.test_mode = test_mode

    def clear(self) -> None:
        self.console.clear()

    def header(self, title: str, current_date: date) -> None:
        date_str = current_date.strftime("%b %-d, %Y")
        if self.test_mode:
            date_str += " [SIM]"
        self.console.print(f"╔{'═' * 44}╗")
        self.console.print(f"║  {title}  |  {date_str:<32} ║")
        self.console.print(f"╚{'═' * 44}╝")
        self.console.print()

    def separator(self) -> None:
        self.console.print("  " + "─" * 42)

    def print(self, text: str = "") -> None:
        self.console.print(f"  {text}")
