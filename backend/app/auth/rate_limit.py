import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AuthRateLimit

LOGIN_EMAIL_LIMIT = 5
LOGIN_IP_LIMIT = 20
LOGIN_WINDOW = timedelta(minutes=15)
SIGNUP_IP_LIMIT = 5
SIGNUP_WINDOW = timedelta(hours=1)


def fingerprint(scope: str, value: str) -> str:
    secret = get_settings().jwt_secret_key.encode("utf-8")
    payload = f"{scope}\x00{value}".encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def _ensure_bucket(db: Session, scope: str, key_hash: str, now: datetime) -> AuthRateLimit:
    db.execute(
        insert(AuthRateLimit)
        .values(scope=scope, key_hash=key_hash, window_started_at=now, attempts=0)
        .on_conflict_do_nothing(index_elements=["scope", "key_hash"])
    )
    bucket = db.scalar(
        select(AuthRateLimit)
        .where(AuthRateLimit.scope == scope)
        .where(AuthRateLimit.key_hash == key_hash)
        .with_for_update()
    )
    if bucket is None:
        raise RuntimeError("Rate-limit bucket could not be loaded")
    return bucket


def check_allowed(db: Session, scope: str, value: str, limit: int, window: timedelta) -> None:
    now = datetime.now(timezone.utc)
    bucket = _ensure_bucket(db, scope, fingerprint(scope, value), now)
    window_end = bucket.window_started_at + window
    if now >= window_end:
        bucket.window_started_at = now
        bucket.attempts = 0
        bucket.blocked_until = None
    if bucket.blocked_until and now < bucket.blocked_until:
        retry_after = max(1, int((bucket.blocked_until - now).total_seconds()))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )
    db.commit()


def record_failure(db: Session, scope: str, value: str, limit: int, window: timedelta) -> None:
    now = datetime.now(timezone.utc)
    bucket = _ensure_bucket(db, scope, fingerprint(scope, value), now)
    window_end = bucket.window_started_at + window
    if now >= window_end:
        bucket.window_started_at = now
        bucket.attempts = 0
        bucket.blocked_until = None
    bucket.attempts += 1
    if bucket.attempts >= limit:
        bucket.blocked_until = bucket.window_started_at + window
    db.commit()


def clear_failures(db: Session, scope: str, value: str) -> None:
    db.execute(
        delete(AuthRateLimit)
        .where(AuthRateLimit.scope == scope)
        .where(AuthRateLimit.key_hash == fingerprint(scope, value))
    )
    db.commit()
