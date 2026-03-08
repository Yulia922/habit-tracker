import argparse

from habit_tracker.cli.app import App
from habit_tracker.cli.navigation import NavigationStack
from habit_tracker.cli.renderer import Renderer
from habit_tracker.db.engine import get_engine
from habit_tracker.db.schema import create_tables
from habit_tracker.fixtures.test_data import load_test_fixtures
from habit_tracker.repositories.completion_repository import SQLiteCompletionRepository
from habit_tracker.repositories.habit_repository import SQLiteHabitRepository
from habit_tracker.services.habit_service import HabitService
from habit_tracker.time_provider.real import RealTimeProvider
from habit_tracker.time_provider.test_mode import TestModeTimeProvider


def main() -> None:
    parser = argparse.ArgumentParser(description="Habit Tracker — track daily and weekly habits")
    parser.add_argument(
        "--test-mode", action="store_true", help="Run with in-memory DB and simulated date (2026-03-01)"
    )
    args = parser.parse_args()

    if args.test_mode:
        engine = get_engine("sqlite:///:memory:")
        time_provider = TestModeTimeProvider()
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

    _habit_service = HabitService(habit_repo, completion_repo, time_provider)

    renderer = Renderer(test_mode=test_mode)
    stack = NavigationStack()

    # Placeholder: push a temporary screen until real screens are built
    from habit_tracker.cli.screens.placeholder import PlaceholderScreen

    stack.push(PlaceholderScreen(habit_repo, completion_repo, time_provider, test_mode))

    app = App(stack, renderer)
    app.run()


if __name__ == "__main__":
    main()
