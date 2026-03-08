from __future__ import annotations

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Refresh
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import calculate_current_streak, calculate_longest_streak
from habit_tracker.time_provider.protocol import TimeProvider


class AnalyticsOverviewScreen:
    def __init__(
        self,
        habits: list[Habit],
        completions_map: dict[int, list[Completion]],
        time: TimeProvider,
    ) -> None:
        self._habits = habits
        self._completions = completions_map
        self._time = time
        self._filter: str = "all"

    def render(self, r: Renderer) -> None:
        r.print("OVERVIEW")
        r.separator()

        filtered = self._get_filtered_habits()

        if not filtered:
            r.print("No habits to show.")
            r.print()
        else:
            r.print(f"{'Habit':<20}{'Period':<10}{'Streak':>7}{'Best':>6}")
            for h in filtered:
                comps = self._completions.get(h.id or 0, [])
                current = calculate_current_streak(h, comps, self._time.today())
                longest = calculate_longest_streak(h, comps)
                period = "daily" if h.periodicity == Periodicity.DAILY else "weekly"
                r.print(f"{h.name:<20}{period:<10}{current:>7}{longest:>6}")
            r.print()

        r.print("Filter: [1] All  [2] Daily  [3] Weekly  [B] Back")

    def _get_filtered_habits(self) -> list[Habit]:
        if self._filter == "daily":
            return [h for h in self._habits if h.periodicity == Periodicity.DAILY]
        if self._filter == "weekly":
            return [h for h in self._habits if h.periodicity == Periodicity.WEEKLY]
        return list(self._habits)

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        if key == "1":
            self._filter = "all"
            return Refresh()
        if key == "2":
            self._filter = "daily"
            return Refresh()
        if key == "3":
            self._filter = "weekly"
            return Refresh()
        return None
