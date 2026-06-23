from datetime import datetime

from sqlalchemy import inspect, text

from app.config import settings
from app.database import SessionLocal, engine
from app.models import User, UserLevel
from app.services.auth_service import hash_password


def run_migrations() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if "exercises" in table_names:
        columns = {column["name"] for column in inspector.get_columns("exercises")}
        if "solution_explanation" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE exercises ADD COLUMN solution_explanation TEXT NOT NULL DEFAULT ''")
                )
        if "hint_signature" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE exercises ADD COLUMN hint_signature TEXT NOT NULL DEFAULT ''")
                )

    if "users" in table_names:
        columns = {column["name"] for column in inspector.get_columns("users")}
        with engine.begin() as connection:
            if "email" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
            if "password_hash" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
            if "last_login_at" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME"))
                connection.execute(
                    text("UPDATE users SET last_login_at = created_at WHERE last_login_at IS NULL")
                )

    ensure_admin_user()


def ensure_admin_user() -> None:
    db = SessionLocal()
    try:
        user = db.get(User, settings.default_user_id)
        if user is None:
            user = User(name="admin", email=settings.admin_email, level=UserLevel.BEGINNER)
            db.add(user)
            db.flush()
        elif user.email is None:
            user.email = settings.admin_email

        user.email = settings.admin_email.strip().lower()

        if user.password_hash is None and settings.admin_password:
            user.password_hash = hash_password(settings.admin_password)

        if user.last_login_at is None:
            user.last_login_at = datetime.utcnow()

        db.commit()
    finally:
        db.close()
