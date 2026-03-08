import argparse

from habit_tracker.cli.app import App
from habit_tracker.cli.navigation import NavigationStack
from habit_tracker.cli.renderer import Renderer
from habit_tracker.cli.screens.add_habit import AddHabitScreen
from habit_tracker.cli.screens.all_habits import AllHabitsScreen
from habit_tracker.cli.screens.analytics_menu import AnalyticsMenuScreen
from habit_tracker.cli.screens.analytics_overview import AnalyticsOverviewScreen
from habit_tracker.cli.screens.analytics_streaks import AnalyticsStreaksScreen
from habit_tracker.cli.screens.analytics_struggling import AnalyticsStrugglingScreen
from habit_tracker.cli.screens.check_off import CheckOffScreen
from habit_tracker.cli.screens.completion_history import CompletionHistoryScreen
from habit_tracker.cli.screens.dashboard import DashboardScreen
from habit_tracker.cli.screens.deactivate_confirm import DeactivateConfirmScreen
from habit_tracker.cli.screens.edit_habit import EditHabitScreen
from habit_tracker.cli.screens.greeting import GreetingScreen
from habit_tracker.cli.screens.habit_detail import HabitDetailScreen
from habit_tracker.cli.screens.skip_day_confirm import SkipDayConfirmScreen
from habit_tracker.db.engine import get_engine
from habit_tracker.db.schema import create_tables
from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.fixtures.test_data import load_test_fixtures
from habit_tracker.repositories.completion_repository import SQLiteCompletionRepository
from habit_tracker.repositories.habit_repository import SQLiteHabitRepository
from habit_tracker.services.habit_service import HabitService
from habit_tracker.services.streak_calculator import calculate_current_streak, get_pending_habits
from habit_tracker.time_provider.protocol import TimeProvider
from habit_tracker.time_provider.real import RealTimeProvider
from habit_tracker.time_provider.test_mode import TestModeTimeProvider


def _load_data(
    habit_repo: SQLiteHabitRepository, completion_repo: SQLiteCompletionRepository
) -> tuple[list[Habit], dict[int, list[Completion]]]:
    habits = habit_repo.list_active()
    completions_map = {h.id: completion_repo.list_for_habit(h.id) for h in habits if h.id is not None}
    return habits, completions_map


def _load_all_data(
    habit_repo: SQLiteHabitRepository, completion_repo: SQLiteCompletionRepository
) -> tuple[list[Habit], dict[int, list[Completion]]]:
    habits = habit_repo.list_all()
    completions_map = {h.id: completion_repo.list_for_habit(h.id) for h in habits if h.id is not None}
    return habits, completions_map


def _build_deactivate_confirm(
    habit: Habit,
    habit_service: HabitService,
    reactivate: bool = False,
) -> DeactivateConfirmScreen:
    def on_confirm() -> None:
        if habit.id is not None:
            if reactivate:
                habit_service.reactivate_habit(habit.id)
            else:
                habit_service.deactivate_habit(habit.id)

    return DeactivateConfirmScreen(habit=habit, on_confirm=on_confirm, reactivate=reactivate)


def _build_edit_habit(
    habit: Habit,
    habit_service: HabitService,
) -> EditHabitScreen:
    return EditHabitScreen(
        habit=habit,
        on_save=lambda hid, n, d, p: habit_service.update_habit(hid, name=n, description=d, periodicity=p),
    )


def _build_habit_detail(
    habit: Habit,
    habit_repo: SQLiteHabitRepository,
    completion_repo: SQLiteCompletionRepository,
    habit_service: HabitService,
    time: TimeProvider,
) -> HabitDetailScreen:
    comps = completion_repo.list_for_habit(habit.id) if habit.id is not None else []
    return HabitDetailScreen(
        habit=habit,
        completions=comps,
        time=time,
        on_check_off=lambda: habit_service.check_off(habit.id) if habit.id else None,
        on_edit=lambda: _build_edit_habit(habit, habit_service),
        on_deactivate=lambda: _build_deactivate_confirm(habit, habit_service),
        on_reactivate=lambda: _build_deactivate_confirm(habit, habit_service, reactivate=True),
    )


def _build_add_habit(
    habit_service: HabitService,
) -> AddHabitScreen:
    return AddHabitScreen(
        on_save=lambda name, desc, period: habit_service.create_habit(name, period, desc),
    )


def _build_all_habits(
    habit_repo: SQLiteHabitRepository,
    completion_repo: SQLiteCompletionRepository,
    habit_service: HabitService,
    time: TimeProvider,
) -> AllHabitsScreen:
    habits, completions_map = _load_all_data(habit_repo, completion_repo)
    return AllHabitsScreen(
        habits=habits,
        completions_map=completions_map,
        time=time,
        on_select=lambda h: _build_habit_detail(h, habit_repo, completion_repo, habit_service, time),
        on_add=lambda: _build_add_habit(habit_service),
    )


def _build_completion_history(
    habit: Habit,
    completion_repo: SQLiteCompletionRepository,
    time: TimeProvider,
) -> CompletionHistoryScreen:
    comps = completion_repo.list_for_habit(habit.id) if habit.id is not None else []
    return CompletionHistoryScreen(habit=habit, completions=comps, time=time)


def _build_analytics_menu(
    habit_repo: SQLiteHabitRepository,
    completion_repo: SQLiteCompletionRepository,
    time: TimeProvider,
) -> AnalyticsMenuScreen:
    def build_overview() -> AnalyticsOverviewScreen:
        habits, completions_map = _load_data(habit_repo, completion_repo)
        return AnalyticsOverviewScreen(habits=habits, completions_map=completions_map, time=time)

    def build_streaks() -> AnalyticsStreaksScreen:
        habits, completions_map = _load_data(habit_repo, completion_repo)
        return AnalyticsStreaksScreen(habits=habits, completions_map=completions_map, time=time)

    def build_struggling() -> AnalyticsStrugglingScreen:
        habits, completions_map = _load_data(habit_repo, completion_repo)
        return AnalyticsStrugglingScreen(habits=habits, completions_map=completions_map, time=time)

    def build_history() -> AllHabitsScreen:
        habits, completions_map = _load_all_data(habit_repo, completion_repo)
        return AllHabitsScreen(
            habits=habits,
            completions_map=completions_map,
            time=time,
            on_select=lambda h: _build_completion_history(h, completion_repo, time),
        )

    return AnalyticsMenuScreen(
        on_overview=build_overview,
        on_streaks=build_streaks,
        on_struggling=build_struggling,
        on_history=build_history,
    )


def _build_check_off(
    habit_repo: SQLiteHabitRepository,
    completion_repo: SQLiteCompletionRepository,
    habit_service: HabitService,
    time: TimeProvider,
) -> CheckOffScreen:
    habits, completions_map = _load_data(habit_repo, completion_repo)
    return CheckOffScreen(
        habits=habits,
        completions_map=completions_map,
        time=time,
        on_complete=lambda hid: habit_service.check_off(hid),
        refresh_data=lambda: _load_data(habit_repo, completion_repo),
    )


def _build_skip_day(
    habit_repo: SQLiteHabitRepository,
    completion_repo: SQLiteCompletionRepository,
    time: TimeProvider,
) -> SkipDayConfirmScreen:
    habits, completions_map = _load_data(habit_repo, completion_repo)

    def on_skip() -> None:
        if hasattr(time, "advance_day"):
            time.advance_day()  # type: ignore[union-attr,unused-ignore]

    return SkipDayConfirmScreen(
        habits=habits,
        completions_map=completions_map,
        time=time,
        on_skip=on_skip,
    )


def _build_dashboard(
    habit_repo: SQLiteHabitRepository,
    completion_repo: SQLiteCompletionRepository,
    habit_service: HabitService,
    time: TimeProvider,
    test_mode: bool,
) -> DashboardScreen:
    habits, completions_map = _load_data(habit_repo, completion_repo)
    return DashboardScreen(
        habits=habits,
        completions_map=completions_map,
        time=time,
        test_mode=test_mode,
        on_check_off=lambda: _build_check_off(habit_repo, completion_repo, habit_service, time),
        on_all_habits=lambda: _build_all_habits(habit_repo, completion_repo, habit_service, time),
        on_analytics=lambda: _build_analytics_menu(habit_repo, completion_repo, time),
        on_manage=lambda: _build_all_habits(habit_repo, completion_repo, habit_service, time),
        on_skip_day=lambda: _build_skip_day(habit_repo, completion_repo, time),
    )


def _build_greeting(
    habit_repo: SQLiteHabitRepository,
    completion_repo: SQLiteCompletionRepository,
    habit_service: HabitService,
    time: TimeProvider,
    test_mode: bool,
) -> GreetingScreen:
    habits, completions_map = _load_data(habit_repo, completion_repo)
    pending = get_pending_habits(habits, completions_map, time.today())
    streaks = {}
    for h in habits:
        if h.id is not None:
            streaks[h.id] = calculate_current_streak(h, completions_map.get(h.id, []), time.today())
    return GreetingScreen(
        habits=habits,
        pending=pending,
        time=time,
        streaks=streaks,
        build_dashboard=lambda: _build_dashboard(habit_repo, completion_repo, habit_service, time, test_mode),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Habit Tracker — track daily and weekly habits")
    parser.add_argument(
        "--test-mode", action="store_true", help="Run with in-memory DB and simulated date (2026-03-01)"
    )
    args = parser.parse_args()

    if args.test_mode:
        engine = get_engine("sqlite:///:memory:")
        time_provider: TimeProvider = TestModeTimeProvider()
        test_mode = True
    else:
        engine = get_engine("sqlite:///habits.db")
        time_provider = RealTimeProvider()
        test_mode = False

    create_tables(engine)

    habit_repo = SQLiteHabitRepository(engine)
    completion_repo = SQLiteCompletionRepository(engine)

    if test_mode:
        load_test_fixtures(habit_repo, completion_repo)

    habit_service = HabitService(habit_repo, completion_repo, time_provider)

    renderer = Renderer(test_mode=test_mode)
    stack = NavigationStack()

    greeting = _build_greeting(habit_repo, completion_repo, habit_service, time_provider, test_mode)
    stack.push(greeting)

    app = App(stack, renderer)
    app.run()


if __name__ == "__main__":
    main()
