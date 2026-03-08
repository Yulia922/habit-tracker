import pytest

from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.exceptions import DuplicateHabitNameError, HabitInactiveError, HabitNotFoundError
from habit_tracker.services.habit_service import HabitService


@pytest.fixture
def service(habit_repo, completion_repo, fake_time):
    return HabitService(habit_repo, completion_repo, fake_time)


class TestCreateHabit:
    def test_returns_persisted_habit(self, service):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        assert habit.id is not None

    def test_raises_on_duplicate_name_case_insensitive(self, service):
        service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        with pytest.raises(DuplicateHabitNameError):
            service.create_habit(name="gym", periodicity=Periodicity.WEEKLY)


class TestUpdateHabit:
    def test_periodicity_change_sets_streak_started_at(self, service, fake_time):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        service.update_habit(habit.id, periodicity=Periodicity.WEEKLY)
        updated = service.get_habit(habit.id)
        assert updated.streak_started_at == fake_time.today()

    def test_name_change_does_not_reset_streak(self, service):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        service.update_habit(habit.id, name="Gym Session")
        updated = service.get_habit(habit.id)
        assert updated.streak_started_at is None

    def test_raises_for_unknown_id(self, service):
        with pytest.raises(HabitNotFoundError):
            service.update_habit(999, name="Ghost")


class TestDeactivateReactivate:
    def test_deactivate_sets_inactive(self, service):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        service.deactivate_habit(habit.id)
        assert service.get_habit(habit.id).status == HabitStatus.INACTIVE

    def test_reactivate_sets_active(self, service):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        service.deactivate_habit(habit.id)
        service.reactivate_habit(habit.id)
        assert service.get_habit(habit.id).status == HabitStatus.ACTIVE


class TestCheckOff:
    def test_creates_completion(self, service):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        completion = service.check_off(habit.id)
        assert completion.habit_id == habit.id

    def test_is_idempotent_same_period(self, service):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        first = service.check_off(habit.id)
        second = service.check_off(habit.id)
        assert first.id == second.id

    def test_inactive_habit_raises(self, service):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        service.deactivate_habit(habit.id)
        with pytest.raises(HabitInactiveError):
            service.check_off(habit.id)

    def test_completion_date_matches_provider(self, service, fake_time):
        habit = service.create_habit(name="Gym", periodicity=Periodicity.DAILY)
        completion = service.check_off(habit.id)
        assert completion.completed_at.date() == fake_time.today()
