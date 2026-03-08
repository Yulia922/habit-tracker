from __future__ import annotations

from collections.abc import Callable

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Refresh
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity


class EditHabitScreen:
    def __init__(
        self,
        habit: Habit,
        on_save: Callable[[int, str | None, str | None, Periodicity | None], Habit] | None = None,
    ) -> None:
        self._habit = habit
        self._on_save = on_save
        self._name = habit.name
        self._description = habit.description
        self._periodicity = habit.periodicity
        self._editing_field: int | None = None
        self._message: str | None = None

    def render(self, r: Renderer) -> None:
        r.print(f"EDIT: {self._habit.name}")
        r.separator()
        r.print()

        if self._editing_field == 1:
            r.print(f"New name [{self._name}]: _")
            r.print()
            r.print("[B] Cancel")
            return

        if self._editing_field == 2:
            r.print(f"New description [{self._description}]: _")
            r.print()
            r.print("[B] Cancel")
            return

        if self._editing_field == 3:
            r.print("New periodicity:")
            r.print("[1] Daily   [2] Weekly")
            r.print("[B] Cancel")
            return

        period_label = "Daily" if self._periodicity == Periodicity.DAILY else "Weekly"
        r.print(f"[1] Name          {self._name}")
        r.print(f"[2] Description   {self._description or '(none)'}")
        r.print(f"[3] Periodicity   {period_label}")
        r.print()
        r.print("\u26a0  Changing periodicity will reset your streak.")
        r.print()

        if self._message:
            r.print(self._message)
            r.print()

        r.print("[ENTER] Save   [B] Cancel")

    def handle_key(self, key: str) -> Action | None:
        if self._editing_field == 3:
            if key == "1":
                self._periodicity = Periodicity.DAILY
                self._editing_field = None
                return Refresh()
            if key == "2":
                self._periodicity = Periodicity.WEEKLY
                self._editing_field = None
                return Refresh()
            if key == keys.BACK:
                self._editing_field = None
                return Refresh()
            return None

        if self._editing_field is not None:
            if key == keys.BACK:
                self._editing_field = None
                return Refresh()
            return None

        if key == keys.BACK:
            return Pop()

        if key == "1":
            self._editing_field = 1
            return Refresh()
        if key == "2":
            self._editing_field = 2
            return Refresh()
        if key == "3":
            self._editing_field = 3
            return Refresh()

        if key == keys.ENTER:
            return self._do_save()

        return None

    def handle_input(self, text: str) -> Action | None:
        stripped = text.strip()
        if self._editing_field == 1:
            if stripped:
                self._name = stripped
            self._editing_field = None
            return Refresh()
        if self._editing_field == 2:
            self._description = stripped
            self._editing_field = None
            return Refresh()
        return None

    def _do_save(self) -> Action | None:
        if self._on_save and self._habit.id is not None:
            name_changed = self._name if self._name != self._habit.name else None
            desc_changed = self._description if self._description != self._habit.description else None
            period_changed = self._periodicity if self._periodicity != self._habit.periodicity else None
            self._on_save(self._habit.id, name_changed, desc_changed, period_changed)
        return Pop()

    @property
    def needs_text_input(self) -> bool:
        return self._editing_field in (1, 2)
