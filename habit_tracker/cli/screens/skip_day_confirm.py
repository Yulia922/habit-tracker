from __future__ import annotations

from collections.abc import Callable

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import get_pending_habits
from habit_tracker.time_provider.protocol import TimeProvider


class SkipDayConfirmScreen:
    def __init__(
        self,
        habits: list[Habit],
        completions_map: dict[int, list[Completion]],
        time: TimeProvider,
        on_skip: Callable[[], None],
    ) -> None:
        self._habits = habits
        self._completions = completions_map
        self._time = time
        self._on_skip = on_skip

    def render(self, r: Renderer) -> None:
        today = self._time.today()
        r.print(f"Skip to next day?  (currently {today.strftime('%b %-d, %Y')})")
        r.separator()
        r.print()

        pending_daily = [
            h for h in get_pending_habits(self._habits, self._completions, today) if h.periodicity == Periodicity.DAILY
        ]

        # Weekly habits only matter if today is Sunday (end of ISO week)
        is_week_boundary = today.weekday() == 6  # Sunday
        pending_weekly = []
        if is_week_boundary:
            pending_weekly = [
                h
                for h in get_pending_habits(self._habits, self._completions, today)
                if h.periodicity == Periodicity.WEEKLY
            ]

        if not pending_daily and not pending_weekly:
            r.print("All done for today! No streaks will be lost.")
        else:
            if pending_daily:
                r.print("These daily habits will be missed:")
                for h in pending_daily:
                    r.print(f"  \u2717 {h.name}")
                r.print()

            if pending_weekly:
                r.print("These weekly habits will be missed (week ending):")
                for h in pending_weekly:
                    r.print(f"  \u2717 {h.name}")
                r.print()

        r.print()
        r.print("[1] Yes, skip to next day   [B] No, go back")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        if key == "1":
            self._on_skip()
            return Pop()
        return None
