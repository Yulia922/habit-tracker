from io import StringIO

from rich.console import Console

from habit_tracker.cli.renderer import Renderer


def capture_render(screen, test_mode: bool = False) -> str:
    """Render a screen to a string for assertion."""
    buf = StringIO()
    console = Console(file=buf, width=50, force_terminal=True)
    renderer = Renderer(console=console, test_mode=test_mode)
    screen.render(renderer)
    return buf.getvalue()
