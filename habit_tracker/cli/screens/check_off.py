from __future__ import annotations

from collections.abc import Callable

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Refresh
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import calculate_current_streak, get_pending_habits
from habit_tracker.time_provider.protocol import TimeProvider


class CheckOffScreen:
    def __init__(
        self,
        habits: list[Habit],
        completions_map: dict[int, list[Completion]],
        time: TimeProvider,
        on_complete: Callable[[int], Completion | None] | None = None,
        refresh_data: Callable[[], tuple[list[Habit], dict[int, list[Completion]]]] | None = None,
    ) -> None:
        self._habits = habits
        self._completions = completions_map
        self._time = time
        self._on_complete = on_complete
        self._refresh_data = refresh_data
        self._message: str | None = None
        self._pending: list[Habit] = []
        self._recalc_pending()

    def _recalc_pending(self) -> None:
        self._pending = get_pending_habits(self._habits, self._completions, self._time.today())

    def render(self, r: Renderer) -> None:
        r.print("Which habit did you complete?")
        r.print()

        if not self._pending:
            r.print("Everything is done for today! ✓")
            r.print()
            r.print("[B] Back")
            return

        daily = [h for h in self._pending if h.periodicity == Periodicity.DAILY]
        weekly = [h for h in self._pending if h.periodicity == Periodicity.WEEKLY]

        idx = 1
        mapping: dict[int, Habit] = {}

        if daily:
            r.print("DAILY")
            for h in daily:
                comps = self._completions.get(h.id or 0, [])
                streak = calculate_current_streak(h, comps, self._time.today())
                r.print(f"[{idx}]  {h.name:<20} (streak: {streak} days)")
                mapping[idx] = h
                idx += 1
            r.print()

        if weekly:
            r.print("WEEKLY")
            for h in weekly:
                comps = self._completions.get(h.id or 0, [])
                streak = calculate_current_streak(h, comps, self._time.today())
                r.print(f"[{idx}]  {h.name:<20} (streak: {streak} weeks)")
                mapping[idx] = h
                idx += 1
            r.print()

        if self._message:
            r.print(self._message)
            r.print()

        r.print("[B] Back")
        self._mapping = mapping

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()

        if keys.is_digit_key(key):
            num = keys.digit_value(key)
            mapping = getattr(self, "_mapping", {})
            habit = mapping.get(num)
            if habit and self._on_complete:
                completion = self._on_complete(habit.id)  # type: ignore[arg-type,unused-ignore]
                if completion:
                    comps = self._completions.get(habit.id or 0, [])
                    streak = calculate_current_streak(habit, comps + [completion], self._time.today())
                    self._message = f'"{habit.name}" — done! ✓  Streak: {streak} days. Keep going!'
                    # Refresh data if available
                    if self._refresh_data:
                        self._habits, self._completions = self._refresh_data()
                    self._recalc_pending()
                    return Refresh()

        return None
