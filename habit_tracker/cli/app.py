from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import NavigationStack, Pop, Push, Quit, Refresh, Replace
from habit_tracker.cli.renderer import Renderer

_ESC = "\x1b"


def _make_session() -> PromptSession[str]:
    kb: KeyBindings = KeyBindings()

    @kb.add("escape")
    def _(event: object) -> None:  # type: ignore[type-arg]
        buf = getattr(event, "current_buffer")
        buf.text = _ESC
        buf.validate_and_handle()

    return PromptSession(key_bindings=kb)


class App:
    def __init__(self, stack: NavigationStack, renderer: Renderer) -> None:
        self._stack = stack
        self._renderer = renderer
        self._session: PromptSession[str] = _make_session()

    def run(self) -> None:
        while True:
            screen = self._stack.current()
            self._renderer.clear()
            screen.render(self._renderer)

            needs_text = getattr(screen, "needs_text_input", False)

            try:
                raw = self._session.prompt("\n  > ")
            except (KeyboardInterrupt, EOFError):
                break

            if needs_text and raw == _ESC:
                action = screen.handle_key(keys.BACK)
            elif needs_text:
                action = screen.handle_input(raw)  # type: ignore[union-attr,unused-ignore]
            else:
                key = raw.strip().lower()
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
                    top = self._stack.current()
                    if hasattr(top, "on_resume"):
                        top.on_resume()  # type: ignore[union-attr,unused-ignore]
            elif isinstance(action, Replace):
                self._stack.replace(action.screen)
            elif isinstance(action, Refresh):
                continue
