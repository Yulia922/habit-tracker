from __future__ import annotations

from typing import Any, Protocol


class NavigationError(Exception):
    pass


class Screen(Protocol):
    def render(self, ctx: Any) -> None: ...
    def handle_key(self, key: str) -> Action | None: ...


class Action:
    """Base for navigation actions returned by screen key handlers."""


class Push(Action):
    def __init__(self, screen: Screen) -> None:
        self.screen = screen


class Pop(Action):
    pass


class Replace(Action):
    def __init__(self, screen: Screen) -> None:
        self.screen = screen


class Quit(Action):
    pass


class Refresh(Action):
    pass


class NavigationStack:
    def __init__(self) -> None:
        self._stack: list[Any] = []

    def push(self, screen: Any) -> None:
        self._stack.append(screen)

    def pop(self) -> None:
        if not self._stack:
            raise NavigationError("Cannot pop from empty navigation stack")
        self._stack.pop()

    def replace(self, screen: Any) -> None:
        if self._stack:
            self._stack[-1] = screen
        else:
            self._stack.append(screen)

    def current(self) -> Any:
        if not self._stack:
            raise NavigationError("Navigation stack is empty")
        return self._stack[-1]

    @property
    def depth(self) -> int:
        return len(self._stack)
