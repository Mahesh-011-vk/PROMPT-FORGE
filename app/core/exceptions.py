"""
PromptForge AI - Custom Domain Exceptions.

Provides domain-specific exceptions mapped to standardized HTTP status codes and error payloads.
"""

from typing import Any


class PromptForgeException(Exception):
    """Base class for all PromptForge domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundException(PromptForgeException):
    """Raised when a requested resource (prompt, template, model) is not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class ValidationErrorException(PromptForgeException):
    """Raised when request payload fails semantic domain validation."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


ValidationException = ValidationErrorException


class RateLimitExceededException(PromptForgeException):
    """Raised when request frequency exceeds assigned quota."""

    def __init__(self, limit: int, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit of {limit} requests per minute exceeded. Please retry in {retry_after} seconds.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"limit": limit, "retry_after": retry_after},
        )


class ModelProviderException(PromptForgeException):
    """Raised when an external or local AI model provider returns an error or is unreachable."""

    def __init__(self, provider: str, original_error: str, is_retryable: bool = True):
        super().__init__(
            message=f"AI Provider '{provider}' encountered an error: {original_error}",
            code="MODEL_PROVIDER_ERROR",
            status_code=503 if is_retryable else 502,
            details={"provider": provider, "retryable": is_retryable},
        )


class SafetyViolationException(PromptForgeException):
    """Raised when user input violates platform safety or child protection rules."""

    def __init__(self, message: str, reason: str, safe_alternative: str | None = None):
        super().__init__(
            message=message,
            code="SAFETY_POLICY_VIOLATION",
            status_code=400,
            details={"reason": reason, "safe_alternative": safe_alternative},
        )


class UnauthorizedException(PromptForgeException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Invalid or expired authentication credentials."):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenException(PromptForgeException):
    """Raised when authenticated user lacks permissions for an operation."""

    def __init__(self, message: str = "Forbidden: Insufficient privileges."):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )
