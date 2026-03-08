from habit_tracker.cli.navigation import Pop
from habit_tracker.cli.screens.deactivate_confirm import DeactivateConfirmScreen
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity
from tests.test_cli.helpers import capture_render


class TestDeactivateConfirmScreen:
    def test_shows_habit_name(self) -> None:
        h = Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
        screen = DeactivateConfirmScreen(habit=h, on_confirm=lambda: None)
        output = capture_render(screen)
        assert "Morning Run" in output

    def test_deactivate_shows_confirmation_prompt(self) -> None:
        h = Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
        screen = DeactivateConfirmScreen(habit=h, on_confirm=lambda: None)
        output = capture_render(screen)
        assert "Deactivate" in output or "deactivate" in output
        assert "Yes" in output or "yes" in output

    def test_reactivate_shows_confirmation_prompt(self) -> None:
        h = Habit(id=1, name="Walk", periodicity=Periodicity.DAILY, status=HabitStatus.INACTIVE)
        screen = DeactivateConfirmScreen(habit=h, on_confirm=lambda: None, reactivate=True)
        output = capture_render(screen)
        assert "Reactivate" in output or "reactivate" in output

    def test_back_returns_pop(self) -> None:
        h = Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
        screen = DeactivateConfirmScreen(habit=h, on_confirm=lambda: None)
        action = screen.handle_key("b")
        assert isinstance(action, Pop)
