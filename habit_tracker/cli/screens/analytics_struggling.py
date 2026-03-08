from __future__ import annotations

from datetime import timedelta

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.protocol import TimeProvider


class AnalyticsStrugglingScreen:
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
        r.print("HABITS THAT NEED ATTENTION")
        r.separator()

        struggling = self._find_struggling()

        if not struggling:
            r.print("All good! No habits need attention right now.")
        else:
            for name, reason in struggling:
                r.print(f"{name:<20} — {reason}")

        r.print()
        r.print("[B] Back")

    def _find_struggling(self) -> list[tuple[str, str]]:
        today = self._time.today()
        results = []

        for h in self._habits:
            comps = self._completions.get(h.id or 0, [])

            if h.periodicity == Periodicity.DAILY:
                # Check last 14 days for missed days
                missed = 0
                for d in range(14):
                    check_date = today - timedelta(days=d)
                    if not any(c.completed_at.date() == check_date for c in comps):
                        missed += 1
                if missed >= 4:
                    results.append((h.name, f"missed {missed} of the last 14 days"))

            elif h.periodicity == Periodicity.WEEKLY:
                # Check last 4 weeks for missed weeks
                missed_weeks = 0
                for w in range(4):
                    week_start = today - timedelta(days=today.weekday() + 7 * w)
                    week_end = week_start + timedelta(days=6)
                    if not any(week_start <= c.completed_at.date() <= week_end for c in comps):
                        missed_weeks += 1
                if missed_weeks >= 2:
                    results.append((h.name, f"missed {missed_weeks} of the last 4 weeks"))

        return results

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        return None
