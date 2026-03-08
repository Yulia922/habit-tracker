from __future__ import annotations

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Push, Quit
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.protocol import TimeProvider


class GreetingScreen:
    def __init__(
        self,
        habits: list[Habit],
        pending: list[Habit],
        time: TimeProvider,
        streaks: dict[int, int] | None = None,
        build_dashboard: object | None = None,
    ) -> None:
        self._habits = habits
        self._pending = pending
        self._time = time
        self._streaks = streaks or {}
        self._build_dashboard = build_dashboard

    def render(self, r: Renderer) -> None:
        r.header("HABIT TRACKER", self._time.today())

        if not self._habits:
            r.print("Welcome! Looks like your first time here.")
            r.print("Let's build some good habits together.")
            r.print()
            r.print("[ENTER] Add your first habit   [Q] Quit")
            return

        if not self._pending:
            r.print("Great work today! Everything is checked off. ✓")
            r.print()
            r.print("[ENTER] Go to dashboard")
            return

        r.print("Here's what needs your attention.")
        r.print()

        daily = [h for h in self._pending if h.periodicity == Periodicity.DAILY]
        weekly = [h for h in self._pending if h.periodicity == Periodicity.WEEKLY]

        if daily:
            r.print("Today:")
            for h in daily:
                streak = self._streaks.get(h.id or 0, 0)
                suffix = f"({streak}-day streak — don't break it!)" if streak > 1 else ""
                r.print(f"  ○  {h.name:<20} {suffix}")
            r.print()

        if weekly:
            r.print("This week:")
            for h in weekly:
                streak = self._streaks.get(h.id or 0, 0)
                suffix = f"({streak}-week streak — did you go yet?)" if streak > 1 else ""
                r.print(f"  ○  {h.name:<20} {suffix}")
            r.print()

        r.print("[ENTER] Go to dashboard")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.QUIT:
            return Quit()
        if key == keys.ENTER and callable(self._build_dashboard):
            return Push(self._build_dashboard())
        return None
