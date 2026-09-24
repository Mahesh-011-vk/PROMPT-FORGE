"""
PromptForge AI - Authentication & RBAC FastAPI Dependencies.
"""

from __future__ import annotations

from collections.abc import Callable
from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.constants import UserRole
from app.core.database import get_db
from app.core.security import (
    AuthenticationException,
    InsufficientPermissionsException,
    decode_access_token,
)
from app.models.user import User


async def get_current_user(
    authorization: str | None = Header(None, description="Bearer <JWT token>"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate bearer JWT token, returning the current user entity."""
    if not authorization:
        raise AuthenticationException("Authorization header required")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationException("Invalid authorization scheme; format must be 'Bearer <token>'")

    token = parts[1]
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Malformed token: missing subject")

    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        raise AuthenticationException("User account associated with token was not found")

    if not user.is_active:
        raise AuthenticationException("User account is deactivated")

    return user


def require_role(*roles: UserRole | str) -> Callable:
    """Dependency factory restricting route access to specified roles."""
    allowed_values = {r.value if isinstance(r, UserRole) else str(r) for r in roles}

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        if user_role_val not in allowed_values:
            raise InsufficientPermissionsException(
                f"Role '{user_role_val}' is not authorized. Required: {', '.join(allowed_values)}"
            )
        return current_user

    return role_checker
