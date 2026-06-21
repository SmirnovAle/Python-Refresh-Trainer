from sqlalchemy import inspect, text

from app.database import engine


def run_migrations() -> None:
    inspector = inspect(engine)
    if "exercises" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("exercises")}
    if "solution_explanation" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE exercises ADD COLUMN solution_explanation TEXT NOT NULL DEFAULT ''")
            )
