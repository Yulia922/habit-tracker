from datetime import date, datetime

from habit_tracker.cli.screens.check_off import CheckOffScreen
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from tests.test_cli.helpers import capture_render


class TestCheckOffScreen:
    def test_lists_only_incomplete_habits(self):
        gym = Habit(id=1, name="Gym", periodicity=Periodicity.DAILY)
        run = Habit(id=2, name="Run", periodicity=Periodicity.DAILY)
        # Gym is already done
        completions_map = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 1))]}
        screen = CheckOffScreen(
            habits=[gym, run],
            completions_map=completions_map,
            time=FakeTimeProvider(date(2026, 3, 1)),
        )
        output = capture_render(screen)
        assert "Run" in output
        assert "Gym" not in output

    def test_shows_all_done_when_nothing_pending(self):
        gym = Habit(id=1, name="Gym", periodicity=Periodicity.DAILY)
        completions_map = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 1))]}
        screen = CheckOffScreen(
            habits=[gym],
            completions_map=completions_map,
            time=FakeTimeProvider(date(2026, 3, 1)),
        )
        output = capture_render(screen)
        assert "done" in output.lower() or "checked off" in output.lower()

    def test_groups_daily_and_weekly(self):
        habits = [
            Habit(id=1, name="Run", periodicity=Periodicity.DAILY),
            Habit(id=2, name="Gym", periodicity=Periodicity.WEEKLY),
        ]
        screen = CheckOffScreen(
            habits=habits,
            completions_map={},
            time=FakeTimeProvider(date(2026, 3, 1)),
        )
        output = capture_render(screen)
        assert "DAILY" in output
        assert "WEEKLY" in output
