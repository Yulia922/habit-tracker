"""Temporary screen until real dashboard/greeting are built."""

from __future__ import annotations

from typing import Any

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Quit
from habit_tracker.cli.renderer import Renderer
from habit_tracker.repositories.completion_repository import CompletionRepository
from habit_tracker.repositories.habit_repository import HabitRepository
from habit_tracker.services.streak_calculator import calculate_current_streak, is_done_for_period
from habit_tracker.time_provider.protocol import TimeProvider


class PlaceholderScreen:
    def __init__(
        self,
        habit_repo: HabitRepository,
        completion_repo: CompletionRepository,
        time: TimeProvider,
        test_mode: bool,
    ) -> None:
        self._habits = habit_repo
        self._completions = completion_repo
        self._time = time
        self._test_mode = test_mode

    def render(self, r: Renderer) -> None:
        today = self._time.today()
        r.header("DASHBOARD", today)

        habits = self._habits.list_active()
        daily = [h for h in habits if h.periodicity.value == "daily"]
        weekly = [h for h in habits if h.periodicity.value == "weekly"]

        if not habits:
            r.print("No habits yet.")
            r.separator()
            r.print("[Q] Quit")
            return

        daily_done = 0
        if daily:
            r.print(f"TODAY")
            r.separator()
            for h in daily:
                completions = self._completions.list_for_habit(h.id)  # type: ignore[arg-type]
                done = is_done_for_period(h, completions, today)
                streak = calculate_current_streak(h, completions, today)
                symbol = "✓" if done else "○"
                if done:
                    daily_done += 1
                r.print(f"{symbol}  {h.name:<20} streak: {streak:>3} days")
            r.print()

        weekly_done = 0
        if weekly:
            r.print(f"THIS WEEK")
            r.separator()
            for h in weekly:
                completions = self._completions.list_for_habit(h.id)  # type: ignore[arg-type]
                done = is_done_for_period(h, completions, today)
                streak = calculate_current_streak(h, completions, today)
                symbol = "✓" if done else "○"
                if done:
                    weekly_done += 1
                r.print(f"{symbol}  {h.name:<20} streak: {streak:>3} weeks")
            r.print()

        r.separator()
        r.print("[Q] Quit")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.QUIT:
            return Quit()
        return None
