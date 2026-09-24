"""
Phase 7 LLM Provider Abstraction & Model Router Tests.
Tests Mock Provider generation, deterministic embeddings, provider dispatch, and circuit-breaker fallback.
"""

import math

import pytest

from app.config.constants import ProviderType
from app.llm.base import LLMResponse
from app.llm.mock_provider import MockProvider, mock_provider
from app.llm.router import ModelRouter


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_a * norm_b)


@pytest.mark.asyncio
async def test_mock_provider_generation():
    """Verify Mock Provider generates structured responses with token and cost metadata."""
    resp = await mock_provider.generate(
        prompt="Design a clean prompt for code review",
        model="mock-forge-v1",
        temperature=0.5,
    )
    assert isinstance(resp, LLMResponse)
    assert resp.provider == ProviderType.MOCK
    assert "mock-forge-v1" in resp.text
    assert resp.input_tokens > 0
    assert resp.output_tokens > 0
    assert resp.finish_reason == "stop"


@pytest.mark.asyncio
async def test_mock_provider_embeddings():
    """Verify Mock Provider generates 768-dim normalized vectors with semantic consistency."""
    vec1 = await mock_provider.embed("A cinematic shot of a futuristic city")
    vec2 = await mock_provider.embed("A cinematic shot of a futuristic city")
    vec3 = await mock_provider.embed("A completely unrelated discussion about tax accounting")

    assert len(vec1) == 768
    # Identical text should have identical vectors (cosine sim == 1.0)
    sim_identical = cosine_similarity(vec1, vec2)
    assert pytest.approx(sim_identical, 0.001) == 1.0

    # Different text should have divergent vectors
    sim_different = cosine_similarity(vec1, vec3)
    assert sim_different < 0.99


@pytest.mark.asyncio
async def test_model_router_provider_dispatch():
    """Verify router correctly routes requests to configured providers."""
    router = ModelRouter()
    provider = router.get_provider("mock")
    assert provider.provider_type == ProviderType.MOCK

    gemini = router.get_provider("gemini")
    assert gemini.provider_type == ProviderType.GEMINI


@pytest.mark.asyncio
async def test_circuit_breaker_failover():
    """Verify router automatically activates fallback when primary provider raises an error."""
    failing_provider = MockProvider(should_fail=True)
    router = ModelRouter()
    # Inject failing provider as mock
    router._providers[ProviderType.MOCK] = failing_provider

    # Now test with another router where primary fails but fallback succeeds
    fallback_router = ModelRouter()
    # Mock Gemini provider that fails
    fallback_router._providers[ProviderType.GEMINI] = failing_provider

    response = await fallback_router.generate(
        prompt="Test circuit breaker",
        model="gemini-2.5-flash",
        allow_fallback=True,
    )

    assert response.fallback_used is True
    assert response.provider == ProviderType.MOCK
    assert "mock-forge-v1" in response.model
