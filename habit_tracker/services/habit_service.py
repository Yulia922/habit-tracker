from datetime import datetime

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.repositories.completion_repository import CompletionRepository
from habit_tracker.repositories.habit_repository import HabitRepository
from habit_tracker.services.exceptions import DuplicateHabitNameError, HabitInactiveError, HabitNotFoundError
from habit_tracker.time_provider.protocol import TimeProvider


class HabitService:
    def __init__(
        self,
        habit_repo: HabitRepository,
        completion_repo: CompletionRepository,
        time: TimeProvider,
    ) -> None:
        self._habits = habit_repo
        self._completions = completion_repo
        self._time = time

    def create_habit(self, name: str, periodicity: Periodicity, description: str = "") -> Habit:
        for existing in self._habits.list_all():
            if existing.name.lower() == name.lower():
                raise DuplicateHabitNameError(f"Habit '{name}' already exists")

        habit = Habit(
            name=name,
            description=description,
            periodicity=periodicity,
            created_at=datetime.combine(self._time.today(), datetime.min.time()),
        )
        return self._habits.save(habit)

    def get_habit(self, habit_id: int) -> Habit:
        habit = self._habits.get(habit_id)
        if habit is None:
            raise HabitNotFoundError(f"No habit with id {habit_id}")
        return habit

    def update_habit(
        self,
        habit_id: int,
        name: str | None = None,
        description: str | None = None,
        periodicity: Periodicity | None = None,
    ) -> Habit:
        habit = self.get_habit(habit_id)

        if name is not None:
            habit.name = name
        if description is not None:
            habit.description = description
        if periodicity is not None and periodicity != habit.periodicity:
            habit.periodicity = periodicity
            habit.streak_started_at = self._time.today()

        self._habits.update(habit)
        return habit

    def deactivate_habit(self, habit_id: int) -> None:
        habit = self.get_habit(habit_id)
        habit.status = HabitStatus.INACTIVE
        self._habits.update(habit)

    def reactivate_habit(self, habit_id: int) -> None:
        habit = self.get_habit(habit_id)
        habit.status = HabitStatus.ACTIVE
        habit.streak_started_at = self._time.today()
        self._habits.update(habit)

    def check_off(self, habit_id: int) -> Completion:
        habit = self.get_habit(habit_id)
        if habit.status == HabitStatus.INACTIVE:
            raise HabitInactiveError(f"Habit '{habit.name}' is inactive")

        today = self._time.today()
        if self._completions.exists_on_date(habit_id, today):
            completions = self._completions.list_for_habit(habit_id)
            return next(c for c in completions if c.completed_at.date() == today)

        completion = Completion(
            habit_id=habit_id,
            completed_at=datetime.combine(today, datetime.min.time()),
        )
        return self._completions.save(completion)
