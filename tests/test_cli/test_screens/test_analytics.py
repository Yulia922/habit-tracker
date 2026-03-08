from datetime import date, datetime

from habit_tracker.cli.navigation import Pop
from habit_tracker.cli.screens.analytics_menu import AnalyticsMenuScreen
from habit_tracker.cli.screens.analytics_overview import AnalyticsOverviewScreen
from habit_tracker.cli.screens.analytics_streaks import AnalyticsStreaksScreen
from habit_tracker.cli.screens.analytics_struggling import AnalyticsStrugglingScreen
from habit_tracker.cli.screens.completion_history import CompletionHistoryScreen
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.time_provider.fake import FakeTimeProvider
from tests.test_cli.helpers import capture_render

_TIME = FakeTimeProvider(date(2026, 3, 8))
_RUN = Habit(id=1, name="Morning Run", periodicity=Periodicity.DAILY)
_GYM = Habit(id=2, name="Gym", periodicity=Periodicity.WEEKLY)


class TestAnalyticsMenu:
    def test_shows_menu_options(self) -> None:
        screen = AnalyticsMenuScreen()
        output = capture_render(screen)
        assert "Overview" in output
        assert "Best streaks" in output or "streaks" in output.lower()
        assert "Back" in output

    def test_back_returns_pop(self) -> None:
        screen = AnalyticsMenuScreen()
        assert isinstance(screen.handle_key("b"), Pop)


class TestAnalyticsOverview:
    def test_shows_habit_with_streak(self) -> None:
        comps = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 8))]}
        screen = AnalyticsOverviewScreen(habits=[_RUN], completions_map=comps, time=_TIME)
        output = capture_render(screen)
        assert "Morning Run" in output

    def test_filter_daily_shows_only_daily(self) -> None:
        screen = AnalyticsOverviewScreen(habits=[_RUN, _GYM], completions_map={}, time=_TIME)
        screen._filter = "daily"
        output = capture_render(screen)
        assert "Morning Run" in output
        assert "Gym" not in output

    def test_filter_weekly_shows_only_weekly(self) -> None:
        screen = AnalyticsOverviewScreen(habits=[_RUN, _GYM], completions_map={}, time=_TIME)
        screen._filter = "weekly"
        output = capture_render(screen)
        assert "Gym" in output
        assert "Morning Run" not in output


class TestAnalyticsStreaks:
    def test_orders_by_longest_streak_desc(self) -> None:
        comps = {
            1: [
                Completion(id=i, habit_id=1, completed_at=datetime(2026, 3, d))
                for i, d in enumerate([5, 6, 7, 8], start=1)
            ],
            2: [Completion(id=10, habit_id=2, completed_at=datetime(2026, 3, 1))],
        }
        screen = AnalyticsStreaksScreen(habits=[_RUN, _GYM], completions_map=comps, time=_TIME)
        output = capture_render(screen)
        run_pos = output.index("Morning Run")
        gym_pos = output.index("Gym")
        assert run_pos < gym_pos


class TestAnalyticsStruggling:
    def test_shows_empty_state_when_none_struggling(self) -> None:
        comps = {1: [Completion(id=1, habit_id=1, completed_at=datetime(2026, 3, 8))]}
        screen = AnalyticsStrugglingScreen(habits=[_RUN], completions_map=comps, time=_TIME)
        output = capture_render(screen)
        assert "all good" in output.lower() or "no habits" in output.lower() or "great" in output.lower()


class TestCompletionHistory:
    def test_shows_habit_name(self) -> None:
        screen = CompletionHistoryScreen(habit=_RUN, completions=[], time=_TIME)
        output = capture_render(screen)
        assert "Morning Run" in output

    def test_paginates(self) -> None:
        comps = [
            Completion(id=i, habit_id=1, completed_at=datetime(2026, 2, d))
            for i, d in enumerate(range(1, 29), start=1)
        ]
        screen = CompletionHistoryScreen(habit=_RUN, completions=comps, time=_TIME, page_size=7)
        output = capture_render(screen)
        assert "page" in output.lower() or "Page" in output

    def test_back_returns_pop(self) -> None:
        screen = CompletionHistoryScreen(habit=_RUN, completions=[], time=_TIME)
        assert isinstance(screen.handle_key("b"), Pop)
