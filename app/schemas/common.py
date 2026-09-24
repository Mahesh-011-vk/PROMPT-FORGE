"""
PromptForge AI - Common API Response and Error Schemas.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error payload for failed requests."""

    code: str = Field(..., description="Machine-readable error classification code")
    message: str = Field(..., description="Human-readable explanation")
    request_id: str | None = Field(default=None, description="Unique trace identifier")
    details: dict[str, Any] = Field(default_factory=dict, description="Contextual error metadata")


class ResponseMeta(BaseModel):
    """Metadata envelope for execution context."""

    request_id: str | None = Field(default=None, description="Correlation identifier")
    process_time_ms: float | None = Field(default=None, description="Request execution latency")
    pagination: dict[str, Any] | None = Field(default=None, description="Pagination details if applicable")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standardized API response envelope."""

    success: bool = Field(default=True, description="Whether the request succeeded")
    data: T | None = Field(default=None, description="Response payload")
    error: ErrorDetail | None = Field(default=None, description="Error detail if request failed")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="Contextual metadata")
