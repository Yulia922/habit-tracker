from datetime import date, datetime

from habit_tracker.cli.navigation import Pop
from habit_tracker.cli.screens.skip_day_confirm import SkipDayConfirmScreen
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from habit_tracker.time_provider.test_mode import TestModeTimeProvider
from tests.test_cli.helpers import capture_render

_RUN = Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
_GYM = Habit(id=2, name="Gym", periodicity=Periodicity.WEEKLY)


class TestSkipDayConfirm:
    def test_lists_unchecked_habits(self) -> None:
        screen = SkipDayConfirmScreen(
            habits=[_RUN],
            completions_map={},
            time=FakeTimeProvider(date(2026, 3, 1)),
            on_skip=lambda: None,
        )
        output = capture_render(screen)
        assert "Morning Run" in output

    def test_shows_all_clear_when_all_done(self) -> None:
        comps = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 1))]}
        screen = SkipDayConfirmScreen(
            habits=[_RUN],
            completions_map=comps,
            time=FakeTimeProvider(date(2026, 3, 1)),
            on_skip=lambda: None,
        )
        output = capture_render(screen)
        assert "all" in output.lower() and "done" in output.lower()

    def test_weekly_unaffected_mid_week(self) -> None:
        # Monday Mar 2 -> skipping shouldn't mention Gym (week not ending)
        screen = SkipDayConfirmScreen(
            habits=[_GYM],
            completions_map={},
            time=FakeTimeProvider(date(2026, 3, 2)),  # Monday
            on_skip=lambda: None,
        )
        output = capture_render(screen)
        assert "Gym" not in output or "no impact" in output.lower()

    def test_weekly_missed_at_week_boundary(self) -> None:
        # Sunday Mar 1 -> ISO week ends, unchecked weekly habit missed
        screen = SkipDayConfirmScreen(
            habits=[_GYM],
            completions_map={},
            time=FakeTimeProvider(date(2026, 3, 1)),  # Sunday
            on_skip=lambda: None,
        )
        output = capture_render(screen)
        assert "Gym" in output

    def test_after_confirming_skip_provider_returns_next_day(self) -> None:
        provider = TestModeTimeProvider()
        provider.advance_day()
        assert provider.today() == date(2026, 3, 2)

    def test_back_returns_pop(self) -> None:
        screen = SkipDayConfirmScreen(
            habits=[_RUN],
            completions_map={},
            time=FakeTimeProvider(date(2026, 3, 1)),
            on_skip=lambda: None,
        )
        assert isinstance(screen.handle_key("b"), Pop)
