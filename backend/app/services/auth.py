from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.models import User as UserModel
from app.db.session import SessionLocal, verify_password


@dataclass(frozen=True)
class DemoUser:
    email: str
    name: str
    role: str
    department: str
    password_hash: str = ""


# Fallback in-memory users — used when DB is unavailable.
# Passwords here are SHA-256 hashed (legacy); DB users use bcrypt.
def _sha256(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


DEMO_USERS: dict[str, DemoUser] = {
    "atul@enterprise.ai": DemoUser(
        email="atul@enterprise.ai", name="Atul", role="admin", department="IT",
        password_hash=_sha256("atul123"),
    ),
    "analyst@enterprise.ai": DemoUser(
        email="analyst@enterprise.ai", name="Enterprise Analyst", role="analyst", department="Operations",
        password_hash=_sha256("analyst123"),
    ),
    "employee@enterprise.ai": DemoUser(
        email="employee@enterprise.ai", name="Enterprise Employee", role="employee", department="HR",
        password_hash=_sha256("employee123"),
    ),
    "viewer@enterprise.ai": DemoUser(
        email="viewer@enterprise.ai", name="Enterprise Viewer", role="viewer", department="Security",
        password_hash=_sha256("viewer123"),
    ),
}


def authenticate_user(email: str, password: str) -> DemoUser | None:
    """Authenticate against DB (bcrypt) first, then fall back to in-memory (SHA-256)."""
    db_user = _get_user_from_db(email.lower())
    if db_user is not None:
        if verify_password(password, db_user.password_hash):
            return db_user
        return None

    # DB unavailable — fall back to hardcoded demo users
    user = DEMO_USERS.get(email.lower())
    if not user:
        return None
    if not hmac.compare_digest(user.password_hash, _sha256(password)):
        return None
    return user


def get_user(email: str) -> DemoUser | None:
    """Look up a user by email. DB first, in-memory fallback."""
    db_user = _get_user_from_db(email.lower())
    if db_user is not None:
        return db_user
    return DEMO_USERS.get(email.lower())


def create_user(email: str, name: str, role: str, department: str, password: str) -> DemoUser | None:
    """Create a new user in the database. Returns None if DB is unavailable or email exists."""
    from app.db.session import hash_password  # avoid circular at module level
    try:
        with SessionLocal() as session:
            exists = session.execute(
                select(UserModel).where(UserModel.email == email.lower())
            ).scalars().first()
            if exists is not None:
                return None  # duplicate
            row = UserModel(
                email=email.lower(),
                name=name,
                role=role,
                department=department,
                password_hash=hash_password(password),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return DemoUser(email=row.email, name=row.name, role=row.role, department=row.department)
    except SQLAlchemyError:
        return None


def _get_user_from_db(email: str) -> DemoUser | None:
    try:
        with SessionLocal() as session:
            row = session.execute(
                select(UserModel).where(UserModel.email == email)
            ).scalars().first()
            if row is None:
                return None
            return DemoUser(
                email=row.email,
                name=row.name,
                role=row.role,
                department=row.department,
                password_hash=row.password_hash,
            )
    except SQLAlchemyError:
        return None


def create_access_token(user: DemoUser) -> str:
    now = int(time.time())
    payload = {
        "sub": user.email,
        "name": user.name,
        "role": user.role,
        "department": user.department,
        "iat": now,
        "exp": now + settings.jwt_expiration_minutes * 60,
    }
    return _encode_jwt(payload)


def decode_access_token(token: str) -> dict | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None

    signing_input = ".".join(parts[:2])
    expected_signature = _sign(signing_input.encode("ascii"))
    if not hmac.compare_digest(parts[2], expected_signature):
        return None

    try:
        payload = json.loads(_b64decode(parts[1]))
    except (ValueError, json.JSONDecodeError):
        return None

    if int(payload.get("exp", 0)) < int(time.time()):
        return None

    return payload


def _encode_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_part = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}"
    signature = _sign(signing_input.encode("ascii"))
    return f"{signing_input}.{signature}"


def _sign(value: bytes) -> str:
    digest = hmac.new(settings.jwt_secret_key.encode("utf-8"), value, hashlib.sha256).digest()
    return _b64encode(digest)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
