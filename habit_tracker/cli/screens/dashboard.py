from __future__ import annotations

from collections.abc import Callable
from typing import Any

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Push, Quit
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import calculate_current_streak, is_done_for_period
from habit_tracker.time_provider.protocol import TimeProvider


class DashboardScreen:
    def __init__(
        self,
        habits: list[Habit],
        completions_map: dict[int, list[Completion]],
        time: TimeProvider,
        test_mode: bool = False,
        on_check_off: Callable[[], Any] | None = None,
        on_all_habits: Callable[[], Any] | None = None,
        on_analytics: Callable[[], Any] | None = None,
        on_manage: Callable[[], Any] | None = None,
        on_skip_day: Callable[[], Any] | None = None,
    ) -> None:
        self._habits = habits
        self._completions = completions_map
        self._time = time
        self._test_mode = test_mode
        self._on_check_off = on_check_off
        self._on_all_habits = on_all_habits
        self._on_analytics = on_analytics
        self._on_manage = on_manage
        self._on_skip_day = on_skip_day

    def render(self, r: Renderer) -> None:
        r.header("DASHBOARD", self._time.today())

        daily = [h for h in self._habits if h.periodicity == Periodicity.DAILY]
        weekly = [h for h in self._habits if h.periodicity == Periodicity.WEEKLY]

        if not self._habits:
            r.print("No habits yet.")
            r.print()
            r.print("[1] Add your first habit   [Q] Quit")
            return

        if daily:
            done_count = sum(
                1 for h in daily if is_done_for_period(h, self._completions.get(h.id or 0, []), self._time.today())
            )
            r.print(f"TODAY              {done_count} / {len(daily)} done")
            r.separator()
            for h in daily:
                comps = self._completions.get(h.id or 0, [])
                done = is_done_for_period(h, comps, self._time.today())
                streak = calculate_current_streak(h, comps, self._time.today())
                symbol = "✓" if done else "○"
                r.print(f"{symbol}  {h.name:<20} streak: {streak:>3} days")
            r.print()

        if weekly:
            done_count = sum(
                1 for h in weekly if is_done_for_period(h, self._completions.get(h.id or 0, []), self._time.today())
            )
            r.print(f"THIS WEEK          {done_count} / {len(weekly)} done")
            r.separator()
            for h in weekly:
                comps = self._completions.get(h.id or 0, [])
                done = is_done_for_period(h, comps, self._time.today())
                streak = calculate_current_streak(h, comps, self._time.today())
                symbol = "✓" if done else "○"
                r.print(f"{symbol}  {h.name:<20} streak: {streak:>3} weeks")
            r.print()

        r.separator()
        r.print("[1] Check off a habit   [2] All habits")
        r.print("[3] Analytics           [4] Manage habits")
        if self._test_mode:
            r.print("[5] Skip to next day    [Q] Quit")
        else:
            r.print("[Q] Quit")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.QUIT:
            return Quit()
        if key == "1" and self._on_check_off:
            return Push(self._on_check_off())
        if key == "2" and self._on_all_habits:
            return Push(self._on_all_habits())
        if key == "3" and self._on_analytics:
            return Push(self._on_analytics())
        if key == "4" and self._on_manage:
            return Push(self._on_manage())
        if key == "5" and self._test_mode and self._on_skip_day:
            return Push(self._on_skip_day())
        return None
