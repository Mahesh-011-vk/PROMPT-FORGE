"""
Phase 8 Prompt Optimizer, Repair, and Translation Unit & Integration Tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.seeder import seed_defaults
from app.main import app
from app.schemas.optimizer import (
    PromptOptimizeRequest,
    PromptRepairRequest,
    PromptTranslateRequest,
)
from app.services.optimizer_service import optimizer_service


@pytest.fixture(autouse=True)
async def setup_optimizer_db():
    """Ensure database is available."""
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_defaults(session)
    yield
    await close_db()


@pytest.mark.asyncio
async def test_optimize_vague_image_prompt():
    """Verify optimization of vague user prompt: 'Make a cinematic image of a car.'"""
    req = PromptOptimizeRequest(
        prompt="Make a cinematic image of a car.",
    )
    result = await optimizer_service.optimize(req)

    assert result.original_prompt == "Make a cinematic image of a car."
    assert "ARRI Alexa" in result.optimized_prompt
    assert "--ar 16:9" in result.optimized_prompt
    assert len(result.why_improved) >= 2
    assert result.score_after > result.score_before
    assert "volumetric" in result.optimized_prompt.lower() or "lighting" in result.optimized_prompt.lower()


@pytest.mark.asyncio
async def test_repair_ambiguous_prompt():
    """Verify deconstruction and repair of ambiguous request: 'make a good website'."""
    req = PromptRepairRequest(
        prompt="make a good website",
    )
    result = await optimizer_service.repair(req)

    assert len(result.identified_ambiguity) >= 3
    assert result.technology_stack is not None
    assert result.design_system is not None
    assert len(result.functional_requirements) >= 2
    assert len(result.explicit_constraints) >= 2
    assert "Lead Full-Stack Architect" in result.repaired_prompt


@pytest.mark.asyncio
async def test_translate_prompt_preserving_tags():
    """Verify translation preserves Midjourney parameters and XML tags."""
    req = PromptTranslateRequest(
        prompt="A cinematic film still of a cyberpunk warrior. Shot on 35mm. --ar 16:9 --v 6.1",
        target_language="Spanish",
    )
    result = await optimizer_service.translate(req)

    assert result.target_language == "Spanish"
    assert "Un fotograma cinematográfico de" in result.translated_prompt
    # Crucial: parameters must not be translated or damaged
    assert "--ar 16:9" in result.translated_prompt
    assert "--v 6.1" in result.translated_prompt


@pytest.mark.asyncio
async def test_api_optimize_endpoint():
    """Verify POST /api/v1/prompts/optimize API gateway endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/prompts/optimize",
            json={"prompt": "A picture of a dog in the park"},
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["success"] is True
        data = payload["data"]
        assert data["score_after"] > data["score_before"]
        assert len(data["why_improved"]) >= 1
