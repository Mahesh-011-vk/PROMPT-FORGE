"""
PromptForge AI - Cryptography and Security Utilities.

Provides password hashing via direct bcrypt and JWT access token handling via python-jose.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config.settings import settings
from app.core.exceptions import PromptForgeException

ALGORITHM = "HS256"


class AuthenticationException(PromptForgeException):
    """Raised when authentication credentials or token are invalid."""

    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
        )


class InsufficientPermissionsException(PromptForgeException):
    """Raised when user lacks the required RBAC role."""

    def __init__(self, message: str = "Operation not permitted for current role"):
        super().__init__(
            message=message,
            code="FORBIDDEN_INSUFFICIENT_PERMISSIONS",
            status_code=403,
        )


def hash_password(password: str) -> str:
    """Hash plaintext password with salted bcrypt."""
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        pw_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a signed JWT access token with expiration timestamp."""
    to_encode = data.copy()
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify and decode a signed JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise AuthenticationException(f"Token verification failed: {e!s}") from e
