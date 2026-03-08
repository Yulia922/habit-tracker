from typing import Protocol

from sqlalchemy import Engine, select
from sqlalchemy.engine import RowMapping

from habit_tracker.db.schema import habits_table
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.habit_status import HabitStatus
from habit_tracker.domain.periodicity import Periodicity


class HabitRepository(Protocol):
    def save(self, habit: Habit) -> Habit: ...
    def get(self, habit_id: int) -> Habit | None: ...
    def list_active(self) -> list[Habit]: ...
    def list_all(self) -> list[Habit]: ...
    def update(self, habit: Habit) -> None: ...


def _row_to_habit(row: RowMapping) -> Habit:
    return Habit(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        periodicity=Periodicity(row["periodicity"]),
        status=HabitStatus(row["status"]),
        created_at=row["created_at"],
        streak_started_at=row["streak_started_at"].date() if row["streak_started_at"] else None,
    )


class SQLiteHabitRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, habit: Habit) -> Habit:
        with self._engine.connect() as conn:
            result = conn.execute(
                habits_table.insert().values(
                    name=habit.name,
                    description=habit.description,
                    periodicity=habit.periodicity.value,
                    status=habit.status.value,
                    created_at=habit.created_at,
                    streak_started_at=habit.streak_started_at,
                )
            )
            conn.commit()
            habit.id = result.inserted_primary_key[0]  # type: ignore[index]
            return habit

    def get(self, habit_id: int) -> Habit | None:
        with self._engine.connect() as conn:
            row = conn.execute(select(habits_table).where(habits_table.c.id == habit_id)).mappings().first()
            return _row_to_habit(row) if row else None

    def list_active(self) -> list[Habit]:
        with self._engine.connect() as conn:
            rows = (
                conn.execute(select(habits_table).where(habits_table.c.status == HabitStatus.ACTIVE.value))
                .mappings()
                .all()
            )
            return [_row_to_habit(r) for r in rows]

    def list_all(self) -> list[Habit]:
        with self._engine.connect() as conn:
            rows = conn.execute(select(habits_table)).mappings().all()
            return [_row_to_habit(r) for r in rows]

    def update(self, habit: Habit) -> None:
        with self._engine.connect() as conn:
            conn.execute(
                habits_table.update()
                .where(habits_table.c.id == habit.id)
                .values(
                    name=habit.name,
                    description=habit.description,
                    periodicity=habit.periodicity.value,
                    status=habit.status.value,
                    streak_started_at=habit.streak_started_at,
                )
            )
            conn.commit()
