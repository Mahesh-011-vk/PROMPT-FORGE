"""
Phase 4 FastAPI Core & API Gateway Integration Tests.
Tests middleware, exception handling, standard envelopes, and v1 endpoints.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.seeder import seed_defaults
from app.main import app


@pytest.fixture(autouse=True)
async def init_test_gateway():
    """Ensure database and seeds are initialized before API calls."""
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_defaults(session)
    yield
    await close_db()


@pytest.mark.asyncio
async def test_root_endpoint_and_headers():
    """Verify root endpoint returns standard envelope and custom timing headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert "x-process-time" in response.headers

        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["app"] == "PromptForge AI"


@pytest.mark.asyncio
async def test_health_and_readiness_probes():
    """Verify liveness and readiness probe responses."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Liveness
        health_resp = await client.get("/api/v1/health")
        assert health_resp.status_code == 200
        health_data = health_resp.json()
        assert health_data["data"]["status"] == "healthy"

        # Readiness
        ready_resp = await client.get("/api/v1/ready")
        assert ready_resp.status_code == 200
        ready_data = ready_resp.json()
        assert ready_data["data"]["status"] == "ready"
        assert ready_data["data"]["database"] == "connected"


@pytest.mark.asyncio
async def test_categories_endpoint_and_404_handling():
    """Verify categories listing and 404 domain error format."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List categories
        list_resp = await client.get("/api/v1/categories?modality=image")
        assert list_resp.status_code == 200
        categories = list_resp.json()["data"]
        assert len(categories) >= 3
        assert any(c["slug"] == "cinematic-image" for c in categories)

        # Get existing category
        cat_resp = await client.get("/api/v1/categories/cinematic-image")
        assert cat_resp.status_code == 200
        assert cat_resp.json()["data"]["name"] == "Cinematic Image"

        # Not found category -> 404 with structured error envelope
        not_found_resp = await client.get("/api/v1/categories/non-existent-category")
        assert not_found_resp.status_code == 404
        error_payload = not_found_resp.json()
        assert error_payload["success"] is False
        assert error_payload["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert "non-existent-category" in error_payload["error"]["message"]


@pytest.mark.asyncio
async def test_models_registry_and_cost_estimation_endpoints():
    """Verify model querying and cost estimation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List models
        models_resp = await client.get("/api/v1/models")
        assert models_resp.status_code == 200
        models = models_resp.json()["data"]
        assert len(models) >= 5

        # Cost estimate
        estimate_resp = await client.post(
            "/api/v1/models/estimate-cost",
            json={
                "model_name": "gemini-2.5-flash",
                "input_tokens": 100000,
                "output_tokens": 50000,
            },
        )
        assert estimate_resp.status_code == 200
        cost_data = estimate_resp.json()["data"]
        assert cost_data["estimated_cost_usd"] > 0.0

        # Model recommendation
        rec_resp = await client.post(
            "/api/v1/models/recommend",
            json={"modality": "image", "requires_vision": True},
        )
        assert rec_resp.status_code == 200
        rec_data = rec_resp.json()["data"]
        assert rec_data["supports_vision"] is True
