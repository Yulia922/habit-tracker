from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity

TEST_MODE_START = date(2026, 3, 1)

TEST_HABITS: list[dict[str, Any]] = [
    {
        "name": "Morning Run",
        "description": "Run at least 20 minutes",
        "periodicity": Periodicity.DAILY,
        # All of Feb except Feb 10 → 19-day streak going into Mar 1
        "completion_offsets": [d for d in range(-28, 0) if d != -19],
    },
    {
        "name": "Read 30 Minutes",
        "description": "Read any book for at least 30 minutes",
        "periodicity": Periodicity.DAILY,
        # Sporadic clusters → 3-day streak going into Mar 1
        "completion_offsets": [-24, -23, -22, -14, -13, -3, -2, -1],
    },
    {
        "name": "Gym",
        "description": "Complete a weight training session",
        "periodicity": Periodicity.WEEKLY,
        # One completion per ISO week for 6 consecutive weeks
        "completion_offsets": [-49, -42, -35, -28, -14, -4],
    },
    {
        "name": "Meditation",
        "description": "10 minutes of mindfulness or breathing exercises",
        "periodicity": Periodicity.DAILY,
        # 10-day streak going into Mar 1
        "completion_offsets": list(range(-10, 0)),
    },
    {
        "name": "No Sugar",
        "description": "Avoid added sugar for the day",
        "periodicity": Periodicity.DAILY,
        # Old January run, then gap, then 4-day streak into Mar 1
        "completion_offsets": [*range(-55, -40), -3, -2, -1],
    },
]


def load_test_fixtures(
    habit_repo: Any,
    completion_repo: Any,
) -> None:
    """Seed repositories with the predefined test habits and completions."""
    for habit_data in TEST_HABITS:
        habit = habit_repo.save(
            Habit(
                name=habit_data["name"],
                description=habit_data["description"],
                periodicity=habit_data["periodicity"],
                created_at=datetime.combine(
                    TEST_MODE_START + timedelta(days=min(habit_data["completion_offsets"])), datetime.min.time()
                ),
            )
        )
        for offset in habit_data["completion_offsets"]:
            completion_date = TEST_MODE_START + timedelta(days=offset)
            completion_repo.save(
                Completion(
                    habit_id=habit.id,
                    completed_at=datetime.combine(completion_date, datetime.min.time()),
                )
            )
