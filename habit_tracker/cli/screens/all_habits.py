from __future__ import annotations

from collections.abc import Callable
from typing import Any

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Push, Quit
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import calculate_current_streak, is_done_for_period
from habit_tracker.time_provider.protocol import TimeProvider


class AllHabitsScreen:
    def __init__(
        self,
        habits: list[Habit],
        completions_map: dict[int, list[Completion]],
        time: TimeProvider,
        on_select: Callable[[Habit], Any] | None = None,
        on_add: Callable[[], Any] | None = None,
    ) -> None:
        self._habits = habits
        self._completions = completions_map
        self._time = time
        self._on_select = on_select
        self._on_add = on_add
        self._mapping: dict[int, Habit] = {}

    def render(self, r: Renderer) -> None:
        r.header("ALL HABITS", self._time.today())

        active = [h for h in self._habits if h.status == HabitStatus.ACTIVE]
        inactive = [h for h in self._habits if h.status == HabitStatus.INACTIVE]

        if not self._habits:
            r.print("No habits yet.")
            r.print()
            r.print("[A] Add new habit   [B] Back   [Q] Quit")
            return

        daily = [h for h in active if h.periodicity == Periodicity.DAILY]
        weekly = [h for h in active if h.periodicity == Periodicity.WEEKLY]

        idx = 1
        mapping: dict[int, Habit] = {}

        if daily:
            r.print("DAILY                   Today     Streak")
            r.separator()
            for h in daily:
                comps = self._completions.get(h.id or 0, [])
                done = is_done_for_period(h, comps, self._time.today())
                streak = calculate_current_streak(h, comps, self._time.today())
                status = "done" if done else "pend"
                symbol = "\u2713" if done else "\u25cb"
                r.print(f"[{idx}]  {h.name:<20} {symbol} {status:<6} {streak:>3} days")
                mapping[idx] = h
                idx += 1
            r.print()

        if weekly:
            r.print("WEEKLY                  Week      Streak")
            r.separator()
            for h in weekly:
                comps = self._completions.get(h.id or 0, [])
                done = is_done_for_period(h, comps, self._time.today())
                streak = calculate_current_streak(h, comps, self._time.today())
                status = "done" if done else "pend"
                symbol = "\u2713" if done else "\u25cb"
                r.print(f"[{idx}]  {h.name:<20} {symbol} {status:<6} {streak:>3} weeks")
                mapping[idx] = h
                idx += 1
            r.print()

        if inactive:
            r.print(f"INACTIVE ({len(inactive)})")
            r.separator()
            for h in inactive:
                r.print(f"[{idx}]  {h.name:<20} (deactivated)")
                mapping[idx] = h
                idx += 1
            r.print()

        r.separator()
        r.print("[A] Add new habit   [B] Back   [Q] Quit")
        self._mapping = mapping

    def handle_key(self, key: str) -> Action | None:
        if key == keys.QUIT:
            return Quit()
        if key == keys.BACK:
            return Pop()
        if key == keys.ADD and self._on_add:
            return Push(self._on_add())
        if keys.is_digit_key(key):
            num = keys.digit_value(key)
            habit = self._mapping.get(num)
            if habit and self._on_select:
                return Push(self._on_select(habit))
        return None
