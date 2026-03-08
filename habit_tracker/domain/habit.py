from dataclasses import dataclass, field
from datetime import date, datetime

from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity


@dataclass
class Habit:
    name: str
    periodicity: Periodicity
    id: int | None = None
    description: str = ""
    status: HabitStatus = HabitStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    streak_started_at: date | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be blank")
