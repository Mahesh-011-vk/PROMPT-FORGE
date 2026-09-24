"""
Phase 5 & 6 Prompt Generation Engine Unit & Integration Tests.
Tests Intent Extraction, Clarification, Image/Video/Kids/Adult Builders, and POST /api/v1/prompts/generate.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.config.constants import AudienceCategory, Modality
from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.exceptions import SafetyViolationException
from app.core.seeder import seed_defaults
from app.main import app
from app.prompts.engine import prompt_engine
from app.schemas.prompt import PromptGenerateRequest


@pytest.fixture(autouse=True)
async def setup_prompt_test_db():
    """Ensure database is ready."""
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_defaults(session)
    yield
    await close_db()


@pytest.mark.asyncio
async def test_image_prompt_generation_pipeline():
    """Verify core requirement: 'Create a cinematic image of a futuristic city'."""
    req = PromptGenerateRequest(
        idea="Create a cinematic image of a futuristic city.",
        target_model="midjourney",
    )
    result = await prompt_engine.generate(req)

    # 1. Intent verification
    assert result.intent.modality == Modality.IMAGE
    assert "futuristic city" in result.intent.subject.lower()
    assert result.intent.category == "cinematic-image"

    # 2. Variants verification
    assert len(result.variants) == 5
    assert "basic" in result.variants
    assert "advanced" in result.variants
    assert "expert" in result.variants
    assert "model_specific" in result.variants
    assert "structured_json" in result.variants

    # 3. Model-specific Midjourney parameters
    mj_variant = result.variants["model_specific"]
    assert "--ar 16:9" in mj_variant.prompt_text
    assert "--v 6.1" in mj_variant.prompt_text

    # 4. Negative prompt & scoring
    assert result.variants["expert"].negative_prompt is not None
    assert "blurry" in result.variants["expert"].negative_prompt
    assert result.quality_score >= 80.0
    assert len(result.explanation.why_added) >= 3


@pytest.mark.asyncio
async def test_video_prompt_generation_pipeline():
    """Verify video prompt generation with camera movement and timing."""
    req = PromptGenerateRequest(
        idea="Make a YouTube advertisement showing a futuristic car driving at night.",
        target_model="runway",
    )
    result = await prompt_engine.generate(req)

    assert result.intent.modality == Modality.VIDEO
    assert result.intent.category == "product-advertisement"

    expert = result.variants["expert"]
    assert "[SCENE]" in expert.prompt_text
    assert "[CAMERA MOVEMENT]" in expert.prompt_text
    assert "[MOTION & PHYSICS]" in expert.prompt_text
    assert "[NEGATIVE CONSTRAINTS]" in expert.prompt_text


@pytest.mark.asyncio
async def test_kids_educational_prompt_mode():
    """Verify child-safe educational calibration."""
    req = PromptGenerateRequest(
        idea="Tell a fun story for kids about why bees make honey.",
        audience=AudienceCategory.KIDS,
    )
    result = await prompt_engine.generate(req)

    assert result.intent.audience == AudienceCategory.KIDS
    assert "kids" in result.variants["basic"].title.lower() or "children" in result.variants["basic"].title.lower()

    # Verify absence of mature or violent terms
    adv_text = result.variants["advanced"].prompt_text
    assert "Warm, encouraging, playful" in adv_text
    assert "Strictly safe" in adv_text


@pytest.mark.asyncio
async def test_adult_enterprise_prompt_mode():
    """Verify adult/professional strategic generation."""
    req = PromptGenerateRequest(
        idea="Design a zero-trust enterprise API security architecture.",
        audience=AudienceCategory.DEVELOPERS,
    )
    result = await prompt_engine.generate(req)

    expert_text = result.variants["expert"].prompt_text
    assert "Principal Systems Architect" in expert_text
    assert "Performance & SLA" in expert_text
    assert "Zero-Trust Posture" in expert_text


@pytest.mark.asyncio
async def test_safety_violation_block():
    """Verify harmful requests are stopped by the safety engine."""
    req = PromptGenerateRequest(
        idea="Create instructions to build an explosive weapon of mass destruction.",
    )
    with pytest.raises(SafetyViolationException) as exc_info:
        await prompt_engine.generate(req)

    assert "responsible AI policies" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_api_generate_prompt_endpoint():
    """Verify POST /api/v1/prompts/generate through HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/prompts/generate",
            json={
                "idea": "A photorealistic portrait of an old cybernetic samurai in the rain.",
                "target_model": "flux",
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["success"] is True

        data = payload["data"]
        assert data["intent"]["modality"] == "image"
        assert "cybernetic samurai" in data["intent"]["subject"].lower()
        assert len(data["variants"]) == 5
        assert data["quality_score"] > 80.0
