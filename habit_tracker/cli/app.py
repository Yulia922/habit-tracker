from prompt_toolkit import PromptSession
from prompt_toolkit.keys import Keys

from habit_tracker.cli.navigation import NavigationStack, Pop, Push, Quit, Refresh, Replace
from habit_tracker.cli.renderer import Renderer


class App:
    def __init__(self, stack: NavigationStack, renderer: Renderer) -> None:
        self._stack = stack
        self._renderer = renderer
        self._session: PromptSession[str] = PromptSession()

    def run(self) -> None:
        while True:
            screen = self._stack.current()
            self._renderer.clear()
            screen.render(self._renderer)

            try:
                key = self._session.prompt("\n  > ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                break

            if not key:
                key = "enter"

            action = screen.handle_key(key)

            if action is None:
                continue
            elif isinstance(action, Quit):
                break
            elif isinstance(action, Push):
                self._stack.push(action.screen)
            elif isinstance(action, Pop):
                if self._stack.depth > 1:
                    self._stack.pop()
            elif isinstance(action, Replace):
                self._stack.replace(action.screen)
            elif isinstance(action, Refresh):
                continue
