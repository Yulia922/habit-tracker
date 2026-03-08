from datetime import date

from habit_tracker.cli.screens.edit_habit import EditHabitScreen
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from tests.test_cli.helpers import capture_render


def _make_screen(habit: Habit | None = None) -> EditHabitScreen:
    h = habit or Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY, description="Run daily")
    return EditHabitScreen(habit=h)


class TestEditHabitScreen:
    def test_shows_current_values(self) -> None:
        output = capture_render(_make_screen())
        assert "Morning Run" in output
        assert "Run daily" in output

    def test_shows_periodicity(self) -> None:
        output = capture_render(_make_screen())
        assert "Daily" in output or "daily" in output

    def test_shows_streak_reset_warning(self) -> None:
        output = capture_render(_make_screen())
        assert "streak" in output.lower()
