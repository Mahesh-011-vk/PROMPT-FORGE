"""
PromptForge AI - Security & Prompt Defense API Endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.common import ResponseEnvelope
from app.schemas.security import (
    SandwichWrapRequest,
    SandwichWrapResponse,
    SecurityScanRequest,
    SecurityScanResponse,
)
from app.security.injection_guard import InjectionGuard
from app.security.pii_scrubber import PIIScrubber
from app.security.sandwich import SandwichDefense

router = APIRouter(prefix="/security", tags=["Security & Guardrails"])


@router.post("/scan")
async def scan_prompt(
    payload: SecurityScanRequest,
) -> ResponseEnvelope[SecurityScanResponse]:
    """Audit prompt for injection attacks, system prompt leaks, and sensitive PII."""
    text = payload.prompt_text
    pii_types: list[str] = []
    sanitized_text = text

    if payload.check_pii:
        sanitized_text, pii_types = PIIScrubber.scrub(text)

    is_safe = True
    risk_score = 0.0
    flags: list[str] = []

    if payload.check_injection:
        is_safe, risk_score, flags = InjectionGuard.scan(sanitized_text)

    # If PII detected, add note to flags
    if pii_types:
        flags.append(f"PII detected and redacted: {', '.join(pii_types)}")

    action = "PASSED" if is_safe else "REJECTED_INJECTION_DETECTED"

    return ResponseEnvelope(
        data=SecurityScanResponse(
            is_safe=is_safe,
            injection_detected=not is_safe,
            injection_risk_score=risk_score,
            pii_detected=pii_types,
            sanitized_text=sanitized_text,
            risk_flags=flags,
            action_taken=action,
        ),
        message="Security audit completed",
    )


@router.post("/wrap-sandwich")
async def wrap_sandwich(
    payload: SandwichWrapRequest,
) -> ResponseEnvelope[SandwichWrapResponse]:
    """Wrap untrusted input in structural XML boundary delimiters with nonces."""
    result = SandwichDefense.wrap(payload.user_input, payload.instruction)
    return ResponseEnvelope(
        data=result,
        message="Defensive delimiter wrapper applied",
    )
