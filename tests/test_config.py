"""
Phase 2 Configuration and Model Registry Unit Tests.
Tests Pydantic Settings, environment overrides, validations, model registry, and logging.
"""

import json
import logging

import pytest
from pydantic import ValidationError

from app.config import (
    Modality,
    ProviderType,
    Settings,
    UserRole,
    model_registry,
    settings,
)
from app.core.logging import JSONFormatter


def test_settings_initialization():
    """Verify settings defaults and types."""
    assert settings.APP_NAME == "PromptForge AI"
    assert settings.PORT == 8000
    assert settings.is_sqlite is True
    assert ProviderType.MOCK in settings.active_providers


def test_port_validation():
    """Verify port constraints (1-65535)."""
    with pytest.raises(ValidationError):
        Settings(PORT=0)

    with pytest.raises(ValidationError):
        Settings(PORT=70000)

    valid_settings = Settings(PORT=9000)
    assert valid_settings.PORT == 9000


def test_log_level_validation():
    """Verify log level validator enforces standard levels."""
    with pytest.raises(ValidationError):
        Settings(LOG_LEVEL="INVALID_LEVEL")

    valid_settings = Settings(LOG_LEVEL="debug")
    assert valid_settings.LOG_LEVEL == "DEBUG"


def test_rate_limit_resolution():
    """Verify role-based rate limit lookups."""
    assert settings.get_rate_limit_for_role(UserRole.ADMIN) == 1200
    assert settings.get_rate_limit_for_role(UserRole.POWER_USER) == 300
    assert settings.get_rate_limit_for_role(UserRole.USER) == 60
    # Fallback to anonymous
    assert settings.get_rate_limit_for_role("UNKNOWN_ROLE") == 15


def test_model_registry_lookup():
    """Verify model specifications can be queried from the registry."""
    spec = model_registry.get("gemini-2.5-flash")
    assert spec is not None
    assert spec.provider == ProviderType.GEMINI
    assert spec.context_window > 1_000_000
    assert Modality.IMAGE in spec.supported_modalities

    # Non-existent model lookup
    missing = model_registry.get("non-existent-model")
    assert missing is None


def test_model_registry_list_and_filter():
    """Verify listing and filtering models by provider and modality."""
    gemini_models = model_registry.list_all(provider=ProviderType.GEMINI)
    assert len(gemini_models) >= 2
    assert all(m.provider == ProviderType.GEMINI for m in gemini_models)

    video_models = model_registry.list_all(modality=Modality.VIDEO)
    assert len(video_models) >= 1
    assert all(Modality.VIDEO in m.supported_modalities for m in video_models)


def test_model_cost_estimation():
    """Verify token pricing calculations."""
    # Free mock model
    free_cost = model_registry.estimate_cost("mock-forge-v1", input_tokens=1000, output_tokens=500)
    assert free_cost == 0.0

    # Gemini 2.5 Flash: $0.075 / 1M in, $0.30 / 1M out
    # 1,000,000 in ($0.075) + 1,000,000 out ($0.30) = $0.375
    cost = model_registry.estimate_cost(
        "gemini-2.5-flash",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )
    assert pytest.approx(cost, 0.001) == 0.375


def test_model_recommendation():
    """Verify intelligent model recommendation heuristics."""
    # Text recommendation
    recommended_text = model_registry.recommend_model(modality=Modality.TEXT)
    assert recommended_text.name in ("gemini-2.5-flash", "gpt-4o", "mock-forge-v1")

    # Local preference recommendation
    recommended_local = model_registry.recommend_model(
        modality=Modality.TEXT,
        prefer_local=True,
    )
    assert recommended_local.provider == ProviderType.OLLAMA


def test_json_formatter_logging():
    """Verify JSON log formatting with custom context fields."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="promptforge.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test structured log",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-12345"
    record.latency_ms = 42

    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert parsed["level"] == "INFO"
    assert parsed["message"] == "Test structured log"
    assert parsed["request_id"] == "req-12345"
    assert parsed["latency_ms"] == 42
