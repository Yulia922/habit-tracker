from datetime import date
from typing import Any

from habit_tracker.cli.screens.dashboard import DashboardScreen
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from tests.test_cli.helpers import capture_render


def _make_dashboard(
    habits: list[Habit] | None = None,
    completions_map: dict[int, list[Any]] | None = None,
    test_mode: bool = False,
    time: FakeTimeProvider | None = None,
) -> DashboardScreen:
    return DashboardScreen(
        habits=habits or [],
        completions_map=completions_map or {},
        time=time or FakeTimeProvider(date(2026, 3, 1)),
        test_mode=test_mode,
    )


class TestDashboard:
    def test_shows_habit_names(self):
        habits = [Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)]
        output = capture_render(_make_dashboard(habits=habits))
        assert "Morning Run" in output

    def test_shows_done_count(self):
        habits = [
            Habit(id=1, name="Gym", periodicity=Periodicity.DAILY),
            Habit(id=2, name="Run", periodicity=Periodicity.DAILY),
        ]
        # Gym is done (has completion on Mar 1)
        from datetime import datetime

        from habit_tracker.domain.completion import Completion

        completions_map = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 1))]}
        output = capture_render(_make_dashboard(habits=habits, completions_map=completions_map))
        assert "1 / 2" in output

    def test_skip_button_present_in_test_mode(self):
        habits = [Habit(id=1, name="Run", periodicity=Periodicity.DAILY)]
        output = capture_render(_make_dashboard(habits=habits, test_mode=True), test_mode=True)
        assert "Skip to next day" in output

    def test_skip_button_absent_in_normal_mode(self):
        output = capture_render(_make_dashboard(test_mode=False))
        assert "Skip to next day" not in output

    def test_empty_state_prompts_to_add(self):
        output = capture_render(_make_dashboard())
        assert "Add" in output or "add" in output

    def test_groups_daily_and_weekly(self):
        habits = [
            Habit(id=1, name="Run", periodicity=Periodicity.DAILY),
            Habit(id=2, name="Gym", periodicity=Periodicity.WEEKLY),
        ]
        output = capture_render(_make_dashboard(habits=habits))
        assert "TODAY" in output
        assert "THIS WEEK" in output
