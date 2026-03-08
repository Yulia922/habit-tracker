from __future__ import annotations

from collections.abc import Callable

from habit_tracker.cli import keys
from habit_tracker.cli.navigation import Action, Pop, Refresh
from habit_tracker.cli.renderer import Renderer
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity


class AddHabitScreen:
    def __init__(
        self,
        on_save: Callable[[str, str, Periodicity], Habit] | None = None,
        on_go_dashboard: Callable[[], object] | None = None,
    ) -> None:
        self._on_save = on_save
        self._on_go_dashboard = on_go_dashboard
        self._step = 1
        self._name = ""
        self._description = ""
        self._periodicity_choice = ""
        self._error: str | None = None
        self._saved_habit: Habit | None = None

    def render(self, r: Renderer) -> None:
        if self._step == 5:
            self._render_success(r)
            return

        if self._step == 4:
            self._render_confirmation(r)
            return

        r.print(f"ADD A NEW HABIT  (step {self._step} of 3)")
        r.separator()
        r.print()

        if self._step == 1:
            if self._error:
                r.print(self._error)
                r.print()
            r.print("Habit name: _")
            r.print()
            r.print("[B] Cancel")

        elif self._step == 2:
            r.print(f"Habit name:   {self._name}")
            r.print("Description:  _")
            r.print()
            r.print("(Optional — press ENTER to skip)")
            r.print("[B] Back")

        elif self._step == 3:
            r.print(f"Habit name:   {self._name}")
            if self._description:
                r.print(f"Description:  {self._description}")
            r.print()
            r.print("How often?")
            r.print("[1] Daily   [2] Weekly")
            r.print("[B] Back")

    def _render_confirmation(self, r: Renderer) -> None:
        r.separator()
        r.print(f"Name:          {self._name}")
        r.print(f"Description:   {self._description or '(none)'}")
        period_label = "Daily" if self._periodicity_choice == "daily" else "Weekly"
        r.print(f"Periodicity:   {period_label}")
        r.separator()
        r.print()
        r.print("[ENTER] Save   [B] Edit   [Q] Cancel")

    def _render_success(self, r: Renderer) -> None:
        name = self._saved_habit.name if self._saved_habit else self._name
        r.print(f'"{name}" added! \u2713')
        r.print()
        r.print("You can check it off right from the dashboard.")
        r.print()
        r.print("[1] Add another   [ENTER] Go to dashboard")

    def handle_key(self, key: str) -> Action | None:
        if self._step == 3:
            if key == "1":
                self._periodicity_choice = "daily"
                self._step = 4
                return Refresh()
            if key == "2":
                self._periodicity_choice = "weekly"
                self._step = 4
                return Refresh()
            if key == keys.BACK:
                self._step = 2
                return Refresh()

        if self._step == 4:
            if key == keys.ENTER:
                return self._do_save()
            if key == keys.BACK:
                self._step = 3
                return Refresh()
            if key == keys.QUIT:
                return Pop()

        if self._step == 5:
            if key == "1":
                self._reset()
                return Refresh()
            if key == keys.ENTER and self._on_go_dashboard:
                return Pop()

        if key == keys.BACK:
            if self._step == 1:
                return Pop()
            self._step -= 1
            return Refresh()

        return None

    def handle_input(self, text: str) -> Action | None:
        if self._step == 1:
            stripped = text.strip()
            if not stripped:
                self._error = "Name cannot be blank."
                return Refresh()
            self._name = stripped
            self._error = None
            self._step = 2
            return Refresh()

        if self._step == 2:
            self._description = text.strip()
            self._step = 3
            return Refresh()

        return None

    def _do_save(self) -> Action | None:
        if self._on_save:
            periodicity = Periodicity.DAILY if self._periodicity_choice == "daily" else Periodicity.WEEKLY
            self._saved_habit = self._on_save(self._name, self._description, periodicity)
        self._step = 5
        return Refresh()

    def _reset(self) -> None:
        self._step = 1
        self._name = ""
        self._description = ""
        self._periodicity_choice = ""
        self._error = None
        self._saved_habit = None

    @property
    def needs_text_input(self) -> bool:
        return self._step in (1, 2)
