from datetime import datetime

import pytest

from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity


class TestHabitConstruction:
    def test_required_fields_and_defaults(self):
        habit = Habit(name="Gym", periodicity=Periodicity.DAILY)

        assert habit.name == "Gym"
        assert habit.periodicity == Periodicity.DAILY
        assert habit.id is None
        assert habit.description == ""
        assert habit.status == HabitStatus.ACTIVE
        assert habit.streak_started_at is None
        assert isinstance(habit.created_at, datetime)

    def test_rejects_blank_name(self):
        with pytest.raises(ValueError, match="name cannot be blank"):
            Habit(name="   ", periodicity=Periodicity.DAILY)

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="name cannot be blank"):
            Habit(name="", periodicity=Periodicity.WEEKLY)

    def test_accepts_all_fields(self):
        created = datetime(2026, 3, 1, 9, 0)
        habit = Habit(
            id=5,
            name="Run",
            description="20 min jog",
            periodicity=Periodicity.WEEKLY,
            status=HabitStatus.INACTIVE,
            created_at=created,
        )

        assert habit.id == 5
        assert habit.description == "20 min jog"
        assert habit.status == HabitStatus.INACTIVE
        assert habit.created_at == created
