from datetime import datetime

import pytest

from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity


class TestHabitRepository:
    def test_save_assigns_id(self, habit_repo):
        habit = habit_repo.save(Habit(name="Gym", periodicity=Periodicity.DAILY))
        assert habit.id is not None

    def test_save_persists_created_at(self, habit_repo):
        created = datetime(2026, 3, 1, 9, 0, 0)
        habit = habit_repo.save(Habit(name="Gym", periodicity=Periodicity.DAILY, created_at=created))
        assert habit_repo.get(habit.id).created_at == created

    def test_get_unknown_id_returns_none(self, habit_repo):
        assert habit_repo.get(999) is None

    def test_list_active_excludes_inactive(self, habit_repo):
        habit_repo.save(Habit(name="Gym", periodicity=Periodicity.DAILY))
        habit_repo.save(Habit(name="Yoga", periodicity=Periodicity.DAILY, status=HabitStatus.INACTIVE))
        result = habit_repo.list_active()
        assert len(result) == 1
        assert result[0].name == "Gym"

    def test_list_all_includes_inactive(self, habit_repo):
        habit_repo.save(Habit(name="Gym", periodicity=Periodicity.DAILY))
        habit_repo.save(Habit(name="Yoga", periodicity=Periodicity.DAILY, status=HabitStatus.INACTIVE))
        assert len(habit_repo.list_all()) == 2

    def test_update_persists_changes(self, habit_repo):
        habit = habit_repo.save(Habit(name="Gym", periodicity=Periodicity.DAILY))
        habit.name = "Gym Session"
        habit_repo.update(habit)
        assert habit_repo.get(habit.id).name == "Gym Session"

    def test_roundtrip_preserves_all_fields(self, habit_repo):
        original = Habit(
            name="Run",
            description="20 min jog",
            periodicity=Periodicity.WEEKLY,
            status=HabitStatus.INACTIVE,
            created_at=datetime(2026, 2, 1, 7, 30),
        )
        saved = habit_repo.save(original)
        loaded = habit_repo.get(saved.id)

        assert loaded.name == "Run"
        assert loaded.description == "20 min jog"
        assert loaded.periodicity == Periodicity.WEEKLY
        assert loaded.status == HabitStatus.INACTIVE
        assert loaded.created_at == datetime(2026, 2, 1, 7, 30)
