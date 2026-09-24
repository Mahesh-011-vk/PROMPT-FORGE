"""
PromptForge AI - Authentication & RBAC API Endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.constants import UserRole
from app.core.auth_deps import get_current_user, require_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
)
from app.schemas.common import ResponseEnvelope
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post("/register")
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[TokenResponse]:
    """Register a new user account and obtain access token."""
    token_resp = await AuthService.register(db=db, payload=payload)
    return ResponseEnvelope(
        data=token_resp,
        message="User registered successfully",
    )


@router.post("/login")
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[TokenResponse]:
    """Authenticate with email and password to receive JWT bearer token."""
    token_resp = await AuthService.login(db=db, payload=payload)
    return ResponseEnvelope(
        data=token_resp,
        message="Login successful",
    )


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
) -> ResponseEnvelope[UserProfileResponse]:
    """Retrieve profile and role info of the currently authenticated user."""
    return ResponseEnvelope(
        data=UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat() if current_user.created_at else None,
        )
    )


@router.get("/admin-check")
async def admin_check(
    admin_user: User = Depends(require_role(UserRole.ADMIN)),
) -> ResponseEnvelope[dict[str, str]]:
    """Verify administrator permissions."""
    return ResponseEnvelope(
        data={"status": "ADMIN_AUTHORIZED", "user_id": admin_user.id},
        message="Admin access granted",
    )
