from __future__ import annotations

from collections.abc import Callable
from typing import Any

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Push
from habit_tracker.cli.renderer import Renderer


class AnalyticsMenuScreen:
    def __init__(
        self,
        on_overview: Callable[[], Any] | None = None,
        on_streaks: Callable[[], Any] | None = None,
        on_struggling: Callable[[], Any] | None = None,
        on_history: Callable[[], Any] | None = None,
    ) -> None:
        self._on_overview = on_overview
        self._on_streaks = on_streaks
        self._on_struggling = on_struggling
        self._on_history = on_history

    def render(self, r: Renderer) -> None:
        r.print("ANALYTICS")
        r.separator()
        r.print()
        r.print("[1] Overview — all habits")
        r.print("[2] Best streaks")
        r.print("[3] Needs attention")
        r.print("[4] Completion history for a habit")
        r.print("[B] Back")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        if key == "1" and self._on_overview:
            return Push(self._on_overview())
        if key == "2" and self._on_streaks:
            return Push(self._on_streaks())
        if key == "3" and self._on_struggling:
            return Push(self._on_struggling())
        if key == "4" and self._on_history:
            return Push(self._on_history())
        return None
