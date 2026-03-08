from dataclasses import dataclass
from datetime import datetime


@dataclass
class Completion:
    habit_id: int
    completed_at: datetime
    id: int | None = None
