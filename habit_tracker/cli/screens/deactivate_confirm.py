from __future__ import annotations

from collections.abc import Callable

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus


class DeactivateConfirmScreen:
    def __init__(
        self,
        habit: Habit,
        on_confirm: Callable[[], None],
        reactivate: bool = False,
    ) -> None:
        self._habit = habit
        self._on_confirm = on_confirm
        self._reactivate = reactivate or habit.status == HabitStatus.INACTIVE

    def render(self, r: Renderer) -> None:
        if self._reactivate:
            r.print(f'Reactivate "{self._habit.name}"?')
            r.print()
            r.print("It will reappear in your daily check-in.")
            r.print("Starting fresh — streak begins at 0.")
            r.print()
            r.print("[1] Yes, reactivate   [B] No, go back")
        else:
            r.print(f'Deactivate "{self._habit.name}"?')
            r.print()
            r.print("It will be hidden from your daily check-in.")
            r.print("Your streak history will be preserved.")
            r.print()
            r.print("[1] Yes, deactivate   [B] No, go back")

    def handle_key(self, key: str) -> Action | None:
        if key == keys.BACK:
            return Pop()
        if key == "1":
            self._on_confirm()
            return Pop()
        return None
