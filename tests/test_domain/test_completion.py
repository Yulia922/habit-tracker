from datetime import datetime

from habit_tracker.domain.completion import Completion


class TestCompletionConstruction:
    def test_stores_habit_id_and_timestamp(self):
        ts = datetime(2026, 3, 1, 8, 45)
        c = Completion(habit_id=3, completed_at=ts)

        assert c.habit_id == 3
        assert c.completed_at == ts
        assert c.id is None
