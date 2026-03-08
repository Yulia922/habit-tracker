import argparse

from habit_tracker.cli.app import App
from habit_tracker.cli.navigation import NavigationStack
from habit_tracker.cli.renderer import Renderer
from habit_tracker.cli.screens.check_off import CheckOffScreen
from habit_tracker.cli.screens.dashboard import DashboardScreen
from habit_tracker.cli.screens.greeting import GreetingScreen
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
