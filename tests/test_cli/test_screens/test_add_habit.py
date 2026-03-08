from habit_tracker.cli.navigation import Pop, Refresh
from habit_tracker.cli.screens.add_habit import AddHabitScreen
from tests.test_cli.helpers import capture_render


class TestAddHabitScreen:
    def test_step1_asks_for_name(self) -> None:
        screen = AddHabitScreen()
        output = capture_render(screen)
        assert "name" in output.lower()
        assert "step 1" in output.lower()

    def test_step2_asks_for_description(self) -> None:
        screen = AddHabitScreen()
        screen._name = "Run"
        screen._step = 2
        output = capture_render(screen)
        assert "description" in output.lower()
        assert "step 2" in output.lower()

    def test_step3_asks_for_periodicity(self) -> None:
        screen = AddHabitScreen()
        screen._name = "Run"
        screen._description = "Daily run"
        screen._step = 3
        output = capture_render(screen)
        assert "Daily" in output
        assert "Weekly" in output

    def test_confirmation_shows_summary(self) -> None:
        screen = AddHabitScreen()
        screen._name = "Run"
        screen._description = "Daily run"
        screen._periodicity_choice = "daily"
        screen._step = 4
        output = capture_render(screen)
        assert "Run" in output
        assert "Daily" in output or "daily" in output

    def test_rejects_blank_name(self) -> None:
        screen = AddHabitScreen()
        screen.handle_input("")
        assert screen._step == 1
        output = capture_render(screen)
        assert "blank" in output.lower() or "empty" in output.lower() or "name" in output.lower()
