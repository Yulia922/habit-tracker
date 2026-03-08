from datetime import date, datetime

from habit_tracker.cli.screens.habit_detail import HabitDetailScreen
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from tests.test_cli.helpers import capture_render


def _make_screen(
    habit: Habit | None = None,
    completions: list[Completion] | None = None,
    time: FakeTimeProvider | None = None,
) -> HabitDetailScreen:
    h = habit or Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
    return HabitDetailScreen(
        habit=h,
        completions=completions or [],
        time=time or FakeTimeProvider(date(2026, 3, 1)),
    )


class TestHabitDetailScreen:
    def test_shows_habit_name(self) -> None:
        output = capture_render(_make_screen())
        assert "Morning Run" in output

    def test_shows_periodicity_and_status(self) -> None:
        output = capture_render(_make_screen())
        assert "Daily" in output or "daily" in output
        assert "Active" in output or "active" in output

    def test_shows_current_streak(self) -> None:
        comps = [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 1))]
        output = capture_render(_make_screen(completions=comps))
        assert "Current streak" in output or "current streak" in output

    def test_shows_longest_streak(self) -> None:
        output = capture_render(_make_screen())
        assert "Longest streak" in output or "longest streak" in output

    def test_shows_total_completions(self) -> None:
        comps = [
            Completion(id=1, habit_id=1, completed_at=datetime(2026, 2, 28)),
            Completion(id=2, habit_id=1, completed_at=datetime(2026, 3, 1)),
        ]
        output = capture_render(_make_screen(completions=comps))
        assert "2" in output

    def test_shows_check_off_option_for_active(self) -> None:
        output = capture_render(_make_screen())
        assert "Check off" in output

    def test_shows_deactivate_option_for_active(self) -> None:
        output = capture_render(_make_screen())
        assert "Deactivate" in output or "deactivate" in output

    def test_shows_reactivate_option_for_inactive(self) -> None:
        h = Habit(id=1, name="Walk", periodicity=Periodicity.DAILY, status=HabitStatus.INACTIVE)
        output = capture_render(_make_screen(habit=h))
        assert "Reactivate" in output or "reactivate" in output
