"""
PromptForge AI - Authentication & User Management Service.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.exceptions import ValidationErrorException
from app.core.security import (
    AuthenticationException,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserPreference
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
)


class AuthService:
    """Service handling credential verification, registration, and JWT creation."""

    @classmethod
    async def register(
        cls,
        db: AsyncSession,
        payload: UserRegisterRequest,
    ) -> TokenResponse:
        """Register a new user, create preferences, and return token."""
        email_clean = payload.email.strip().lower()

        # Check existing
        existing_stmt = select(User).where(User.email == email_clean)
        existing_res = await db.execute(existing_stmt)
        if existing_res.scalars().first():
            raise ValidationErrorException(f"User with email '{email_clean}' is already registered")

        user = User(
            email=email_clean,
            hashed_password=hash_password(payload.password),
            role=payload.role,
            is_active=True,
        )
        db.add(user)
        await db.flush()

        pref = UserPreference(
            user_id=user.id,
            enable_memory=True,
            default_modality="text",
            default_model="gpt-4o",
        )
        db.add(pref)
        await db.commit()
        await db.refresh(user)

        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role.value}
        )

        return TokenResponse(
            access_token=access_token,
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=UserProfileResponse(
                id=user.id,
                email=user.email,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None,
            ),
        )

    @classmethod
    async def login(
        cls,
        db: AsyncSession,
        payload: UserLoginRequest,
    ) -> TokenResponse:
        """Authenticate user by email and password, generating an access token."""
        email_clean = payload.email.strip().lower()

        stmt = select(User).where(User.email == email_clean)
        res = await db.execute(stmt)
        user = res.scalars().first()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")

        if not user.is_active:
            raise AuthenticationException("User account is deactivated")

        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role.value}
        )

        return TokenResponse(
            access_token=access_token,
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=UserProfileResponse(
                id=user.id,
                email=user.email,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None,
            ),
        )

    @classmethod
    async def get_user_profile(cls, db: AsyncSession, user_id: str) -> dict[str, Any]:
        """Fetch user profile."""
        stmt = select(User).where(User.id == user_id)
        res = await db.execute(stmt)
        user = res.scalars().first()
        if not user:
            raise AuthenticationException("User not found")

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
