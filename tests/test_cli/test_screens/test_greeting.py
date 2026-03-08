from datetime import date, datetime

from habit_tracker.cli.screens.greeting import GreetingScreen
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from tests.test_cli.helpers import capture_render


class TestGreetingScreen:
    def test_first_time_message_when_no_habits(self):
        screen = GreetingScreen(habits=[], pending=[], time=FakeTimeProvider(date(2026, 3, 1)))
        output = capture_render(screen)
        assert "first time" in output.lower()

    def test_lists_pending_daily_habits(self):
        run = Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
        screen = GreetingScreen(
            habits=[run],
            pending=[run],
            time=FakeTimeProvider(date(2026, 3, 1)),
            streaks={1: 5},
        )
        output = capture_render(screen)
        assert "Morning Run" in output
        assert "5" in output

    def test_lists_pending_weekly_habits(self):
        gym = Habit(id=1, name="Gym", periodicity=Periodicity.WEEKLY)
        screen = GreetingScreen(
            habits=[gym],
            pending=[gym],
            time=FakeTimeProvider(date(2026, 3, 1)),
            streaks={1: 3},
        )
        output = capture_render(screen)
        assert "Gym" in output

    def test_all_done_message(self):
        run = Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
        screen = GreetingScreen(
            habits=[run],
            pending=[],
            time=FakeTimeProvider(date(2026, 3, 1)),
        )
        output = capture_render(screen)
        assert "done" in output.lower() or "checked off" in output.lower()

    def test_sim_badge_in_test_mode(self):
        screen = GreetingScreen(habits=[], pending=[], time=FakeTimeProvider(date(2026, 3, 1)))
        output = capture_render(screen, test_mode=True)
        assert "[SIM]" in output
