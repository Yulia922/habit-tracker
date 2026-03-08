from datetime import date

import pytest
from sqlalchemy import create_engine

from habit_tracker.db.schema import create_tables
from habit_tracker.repositories.habit_repository import SQLiteHabitRepository
from habit_tracker.repositories.completion_repository import SQLiteCompletionRepository
from habit_tracker.time_provider.fake import FakeTimeProvider


@pytest.fixture
def engine():
    e = create_engine("sqlite:///:memory:")
    create_tables(e)
    return e


@pytest.fixture
def habit_repo(engine):
    return SQLiteHabitRepository(engine)


@pytest.fixture
def completion_repo(engine):
    return SQLiteCompletionRepository(engine)


@pytest.fixture
def fake_time():
    return FakeTimeProvider(date(2026, 3, 1))
