from sqlalchemy import Column, DateTime, Engine, ForeignKey, Integer, MetaData, String, Table

metadata = MetaData()

habits_table = Table(
    "habits",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False, default=""),
    Column("periodicity", String, nullable=False),
    Column("status", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("streak_started_at", DateTime, nullable=True),
)

completions_table = Table(
    "completions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("habit_id", Integer, ForeignKey("habits.id"), nullable=False),
    Column("completed_at", DateTime, nullable=False),
)


def create_tables(engine: Engine) -> None:
    metadata.create_all(engine)
