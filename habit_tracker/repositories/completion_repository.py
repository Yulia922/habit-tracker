from datetime import date, datetime, timedelta
from typing import Protocol

from sqlalchemy import Engine, and_, select

from habit_tracker.db.schema import completions_table
from habit_tracker.domain.completion import Completion


class CompletionRepository(Protocol):
    def save(self, completion: Completion) -> Completion: ...
    def list_for_habit(self, habit_id: int) -> list[Completion]: ...
    def exists_on_date(self, habit_id: int, target_date: date) -> bool: ...


class SQLiteCompletionRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, completion: Completion) -> Completion:
        with self._engine.connect() as conn:
            result = conn.execute(
                completions_table.insert().values(
                    habit_id=completion.habit_id,
                    completed_at=completion.completed_at,
                )
            )
            conn.commit()
            completion.id = result.inserted_primary_key[0]  # type: ignore[index]
            return completion

    def list_for_habit(self, habit_id: int) -> list[Completion]:
        with self._engine.connect() as conn:
            rows = (
                conn.execute(
                    select(completions_table)
                    .where(completions_table.c.habit_id == habit_id)
                    .order_by(completions_table.c.completed_at.desc())
                )
                .mappings()
                .all()
            )
            return [Completion(id=r["id"], habit_id=r["habit_id"], completed_at=r["completed_at"]) for r in rows]

    def exists_on_date(self, habit_id: int, target_date: date) -> bool:
        """Check if a completion exists anywhere within the given calendar day."""
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        with self._engine.connect() as conn:
            row = conn.execute(
                select(completions_table.c.id).where(
                    and_(
                        completions_table.c.habit_id == habit_id,
                        completions_table.c.completed_at >= day_start,
                        completions_table.c.completed_at < day_end,
                    )
                )
            ).first()
            return row is not None
