from __future__ import annotations

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import calculate_longest_streak
from habit_tracker.time_provider.protocol import TimeProvider


class AnalyticsStreaksScreen:
    def __init__(
        self,
        habits: list[Habit],
        completions_map: dict[int, list[Completion]],
        time: TimeProvider,
    ) -> None:
        self._habits = habits
        self._completions = completions_map
        self._time = time

    def render(self, r: Renderer) -> None:
        r.print("YOUR BEST STREAKS (all time)")
        r.separator()

        ranked = []
        for h in self._habits:
            comps = self._completions.get(h.id or 0, [])
            longest = calculate_longest_streak(h, comps)
            ranked.append((h, longest))

        ranked.sort(key=lambda x: x[1], reverse=True)

        for i, (h, streak) in enumerate(ranked, 1):
            unit = "days" if h.periodicity == Periodicity.DAILY else "weeks"
            period = "daily" if h.periodicity == Periodicity.DAILY else "weekly"
            r.print(f"#{i}  {h.name:<20}{streak:>3} {unit:<6} ({period})")

        if not ranked:
            r.print("No habits yet.")

        r.print()
        r.print("[B] Back")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        return None
