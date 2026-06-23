import logging
import re
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Progress, User

logger = logging.getLogger(__name__)

BCRYPT_ROUNDS = 12
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegistrationError(Exception):
    pass


class RegistrationDisabledError(RegistrationError):
    pass


class UserLimitError(RegistrationError):
    pass


class EmailTakenError(RegistrationError):
    pass


class InvalidRegistrationError(RegistrationError):
    pass


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode()


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), password_hash.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(hours=settings.jwt_expire_hours)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    return int(payload["sub"])


def normalize_email(email: str) -> str:
    return email.strip().lower()


def touch_last_login(db: Session, user: User) -> None:
    user.last_login_at = datetime.utcnow()
    db.commit()


def register_user(db: Session, *, name: str, email: str, password: str) -> User:
    if not settings.registration_enabled:
        raise RegistrationDisabledError("Регистрация отключена")

    cleaned_name = name.strip()
    if len(cleaned_name) < 2:
        raise InvalidRegistrationError("Имя должно быть не короче 2 символов")

    normalized_email = normalize_email(email)
    if not EMAIL_PATTERN.match(normalized_email):
        raise InvalidRegistrationError("Некорректный email")

    if normalize_email(settings.admin_email) == normalized_email:
        raise InvalidRegistrationError("Этот email зарезервирован")

    total_users = db.query(User).count()
    if total_users >= settings.max_users:
        raise UserLimitError(f"Достигнут лимит пользователей ({settings.max_users})")

    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing is not None:
        raise EmailTakenError("Email уже зарегистрирован")

    now = datetime.utcnow()
    user = User(
        name=cleaned_name[:100],
        email=normalized_email,
        password_hash=hash_password(password),
        last_login_at=now,
        created_at=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def cleanup_inactive_accounts(db: Session) -> int:
    if settings.inactive_account_days <= 0:
        return 0

    cutoff = datetime.utcnow() - timedelta(days=settings.inactive_account_days)
    protected_email = normalize_email(settings.admin_email)

    candidates = (
        db.query(User)
        .filter(User.email != protected_email)
        .all()
    )

    deleted = 0
    for user in candidates:
        last_seen = user.last_login_at or user.created_at
        if last_seen >= cutoff:
            continue
        db.query(Progress).filter(Progress.user_id == user.id).delete()
        db.delete(user)
        deleted += 1

    if deleted:
        db.commit()
        logger.info("Removed %s inactive user account(s)", deleted)

    return deleted
