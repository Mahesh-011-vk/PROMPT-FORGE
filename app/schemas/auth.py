"""
PromptForge AI - Authentication & RBAC Schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.config.constants import UserRole


class UserRegisterRequest(BaseModel):
    """Payload to register a new user account."""

    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        json_schema_extra={"example": "developer@promptforge.ai"},
    )
    password: str = Field(..., min_length=8, description="Minimum 8 characters password")
    role: UserRole = Field(UserRole.USER, description="Assigned role: USER, POWER_USER, or ADMIN")


class UserLoginRequest(BaseModel):
    """Payload to authenticate and retrieve access token."""

    email: str = Field(..., json_schema_extra={"example": "developer@promptforge.ai"})
    password: str = Field(..., min_length=1)


class UserProfileResponse(BaseModel):
    """Public profile of an authenticated user."""

    id: str
    email: str
    role: str
    is_active: bool
    created_at: str | None = None


class TokenResponse(BaseModel):
    """JWT bearer token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserProfileResponse
