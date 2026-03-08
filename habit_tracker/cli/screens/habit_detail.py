from __future__ import annotations

from collections.abc import Callable
from typing import Any

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Push, Refresh
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import calculate_current_streak, calculate_longest_streak
from habit_tracker.time_provider.protocol import TimeProvider


class HabitDetailScreen:
    def __init__(
        self,
        habit: Habit,
        completions: list[Completion],
        time: TimeProvider,
        on_check_off: Callable[[], Any] | None = None,
        on_edit: Callable[[], Any] | None = None,
        on_deactivate: Callable[[], Any] | None = None,
        on_reactivate: Callable[[], Any] | None = None,
    ) -> None:
        self._habit = habit
        self._completions = completions
        self._time = time
        self._on_check_off = on_check_off
        self._on_edit = on_edit
        self._on_deactivate = on_deactivate
        self._on_reactivate = on_reactivate

    def render(self, r: Renderer) -> None:
        r.header(self._habit.name, self._time.today())

        period_label = "Daily" if self._habit.periodicity == Periodicity.DAILY else "Weekly"
        status_label = "Active" if self._habit.status == HabitStatus.ACTIVE else "Inactive"
        r.print(f"Description:    {self._habit.description or '(none)'}")
        r.print(f"Periodicity:    {period_label}  |  Status: {status_label}")
        r.print(f"Added:          {self._habit.created_at.strftime('%b %d, %Y')}")
        r.print()

        current = calculate_current_streak(self._habit, self._completions, self._time.today())
        longest = calculate_longest_streak(self._habit, self._completions)
        total = len(self._completions)
        unit = "days" if self._habit.periodicity == Periodicity.DAILY else "weeks"

        r.print(f"Current streak:    {current} {unit}")
        r.print(f"Longest streak:    {longest} {unit}")
        r.print(f"Total completions: {total}")
        r.print()

        if self._completions:
            r.print("Recent:")
            sorted_comps = sorted(self._completions, key=lambda c: c.completed_at, reverse=True)
            recent = sorted_comps[:10]
            line = "  "
            for c in recent:
                line += f"\u2713 {c.completed_at.strftime('%b %-d')}  "
            r.print(line.rstrip())
            r.print()

        r.separator()
        if self._habit.status == HabitStatus.ACTIVE:
            r.print("[1] Check off today   [2] Edit")
            r.print("[3] Deactivate        [B] Back")
        else:
            r.print("[1] Reactivate        [2] Edit")
            r.print("[B] Back")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        if self._habit.status == HabitStatus.ACTIVE:
            if key == "1" and self._on_check_off:
                self._on_check_off()
                return Refresh()
            if key == "2" and self._on_edit:
                return Push(self._on_edit())
            if key == "3" and self._on_deactivate:
                return Push(self._on_deactivate())
        else:
            if key == "1" and self._on_reactivate:
                return Push(self._on_reactivate())
            if key == "2" and self._on_edit:
                return Push(self._on_edit())
        return None
