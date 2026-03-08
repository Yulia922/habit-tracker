from datetime import date, datetime

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity


class TestCompletionRepository:
    def _make_habit(self, habit_repo, name="Gym"):
        return habit_repo.save(Habit(name=name, periodicity=Periodicity.DAILY))

    def test_save_assigns_id(self, habit_repo, completion_repo):
        habit = self._make_habit(habit_repo)
        c = completion_repo.save(Completion(habit_id=habit.id, completed_at=datetime(2026, 3, 1, 9, 0)))
        assert c.id is not None

    def test_save_persists_exact_timestamp(self, habit_repo, completion_repo):
        habit = self._make_habit(habit_repo)
        ts = datetime(2026, 3, 1, 8, 45, 30)
        completion_repo.save(Completion(habit_id=habit.id, completed_at=ts))
        result = completion_repo.list_for_habit(habit.id)
        assert result[0].completed_at == ts

    def test_list_for_habit_ordered_newest_first(self, habit_repo, completion_repo):
        habit = self._make_habit(habit_repo)
        completion_repo.save(Completion(habit_id=habit.id, completed_at=datetime(2026, 3, 1)))
        completion_repo.save(Completion(habit_id=habit.id, completed_at=datetime(2026, 3, 3)))
        results = completion_repo.list_for_habit(habit.id)
        assert results[0].completed_at > results[1].completed_at

    def test_list_for_habit_isolates_by_habit(self, habit_repo, completion_repo):
        h1 = self._make_habit(habit_repo, "Gym")
        h2 = self._make_habit(habit_repo, "Run")
        completion_repo.save(Completion(habit_id=h1.id, completed_at=datetime(2026, 3, 1)))
        completion_repo.save(Completion(habit_id=h2.id, completed_at=datetime(2026, 3, 1)))
        assert len(completion_repo.list_for_habit(h1.id)) == 1

    def test_exists_on_date_true(self, habit_repo, completion_repo):
        habit = self._make_habit(habit_repo)
        completion_repo.save(Completion(habit_id=habit.id, completed_at=datetime(2026, 3, 1, 9, 0)))
        assert completion_repo.exists_on_date(habit.id, date(2026, 3, 1))

    def test_exists_on_date_false_different_day(self, habit_repo, completion_repo):
        habit = self._make_habit(habit_repo)
        completion_repo.save(Completion(habit_id=habit.id, completed_at=datetime(2026, 3, 1, 9, 0)))
        assert not completion_repo.exists_on_date(habit.id, date(2026, 3, 2))

    def test_exists_on_date_false_no_completions(self, habit_repo, completion_repo):
        habit = self._make_habit(habit_repo)
        assert not completion_repo.exists_on_date(habit.id, date(2026, 3, 1))
