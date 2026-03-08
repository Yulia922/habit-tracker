from datetime import date, datetime

from habit_tracker.cli.screens.all_habits import AllHabitsScreen
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from tests.test_cli.helpers import capture_render


def _make_screen(
    habits: list[Habit] | None = None,
    completions_map: dict[int, list[Completion]] | None = None,
    time: FakeTimeProvider | None = None,
) -> AllHabitsScreen:
    return AllHabitsScreen(
        habits=habits or [],
        completions_map=completions_map or {},
        time=time or FakeTimeProvider(date(2026, 3, 1)),
    )


class TestAllHabitsScreen:
    def test_groups_daily_and_weekly(self) -> None:
        habits = [
            Habit(id=1, name="Run", periodicity=Periodicity.DAILY),
            Habit(id=2, name="Gym", periodicity=Periodicity.WEEKLY),
        ]
        output = capture_render(_make_screen(habits=habits))
        assert "DAILY" in output
        assert "WEEKLY" in output

    def test_shows_inactive_section(self) -> None:
        habits = [
            Habit(id=1, name="Run", periodicity=Periodicity.DAILY),
            Habit(
                id=2,
                name="Walk",
                periodicity=Periodicity.DAILY,
                status=HabitStatus.INACTIVE,
            ),
        ]
        output = capture_render(_make_screen(habits=habits))
        assert "INACTIVE" in output
        assert "Walk" in output

    def test_shows_done_status(self) -> None:
        habits = [Habit(id=1, name="Run", periodicity=Periodicity.DAILY)]
        completions = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 1))]}
        output = capture_render(_make_screen(habits=habits, completions_map=completions))
        assert "done" in output.lower()

    def test_shows_pending_status(self) -> None:
        habits = [Habit(id=1, name="Run", periodicity=Periodicity.DAILY)]
        output = capture_render(_make_screen(habits=habits))
        assert "pend" in output.lower()

    def test_shows_streak(self) -> None:
        habits = [Habit(id=1, name="Run", periodicity=Periodicity.DAILY)]
        completions = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 1))]}
        output = capture_render(_make_screen(habits=habits, completions_map=completions))
        assert "1" in output

    def test_empty_state(self) -> None:
        output = capture_render(_make_screen())
        assert "No habits" in output or "no habits" in output
