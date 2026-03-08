from __future__ import annotations

from itertools import groupby

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Refresh
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.time_provider.protocol import TimeProvider


class CompletionHistoryScreen:
    def __init__(
        self,
        habit: Habit,
        completions: list[Completion],
        time: TimeProvider,
        page_size: int = 7,
    ) -> None:
        self._habit = habit
        self._completions = sorted(completions, key=lambda c: c.completed_at, reverse=True)
        self._time = time
        self._page_size = page_size
        self._page = 0

    @property
    def _total_pages(self) -> int:
        if not self._completions:
            return 1
        return max(1, (len(self._completions) + self._page_size - 1) // self._page_size)

    def render(self, r: Renderer) -> None:
        r.print(f"HISTORY: {self._habit.name}           page {self._page + 1} / {self._total_pages}")
        r.separator()

        if not self._completions:
            r.print("No completions yet.")
            r.print()
            r.print("[B] Back")
            return

        start = self._page * self._page_size
        end = start + self._page_size
        page_comps = self._completions[start:end]

        for month_key, group in groupby(page_comps, key=lambda c: c.completed_at.strftime("%B %Y")):
            r.print(month_key)
            line = "  "
            for c in group:
                line += f"\u2713 {c.completed_at.strftime('%b %-d')}  "
            r.print(line.rstrip())
            r.print()

        nav_parts = []
        if self._page > 0:
            nav_parts.append("[P] Prev page")
        if self._page < self._total_pages - 1:
            nav_parts.append("[N] Next page")
        nav_parts.append("[B] Back")
        r.print("   ".join(nav_parts))

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        if key == keys.NEXT_PAGE and self._page < self._total_pages - 1:
            self._page += 1
            return Refresh()
        if key == keys.PREV_PAGE and self._page > 0:
            self._page -= 1
            return Refresh()
        return None
