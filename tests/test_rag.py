"""
Phase 10 & 11 RAG, Vector Search, and Deduplication Unit & Integration Tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.seeder import seed_defaults
from app.main import app
from app.models.prompt import Prompt
from app.rag.chunker import text_chunker
from app.rag.deduplicator import prompt_deduplicator
from app.rag.retriever import knowledge_retriever


@pytest.fixture(autouse=True)
async def setup_rag_db():
    """Ensure database and seeded knowledge base are available."""
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_defaults(session)
        # Ingest knowledge documents for tests
        await knowledge_retriever.ingest_directory("knowledge", session)
    yield
    await close_db()


def test_text_chunker_splitting():
    """Verify recursive character chunker splits long paragraphs with overlap."""
    chunker = text_chunker.__class__(chunk_size=120, chunk_overlap=20)
    sample_text = (
        "Paragraph One introduces the primary instruction architecture.\n\n"
        "Paragraph Two discusses how volumetric lighting and camera lenses shape diffusion outputs. "
        "It provides concrete recommendations for 35mm anamorphic primes and Hasselblad sensor sizes.\n\n"
        "Paragraph Three covers negative constraints and format anchoring."
    )
    chunks = chunker.split_text(sample_text)
    assert len(chunks) >= 2
    assert "Paragraph One" in chunks[0]


@pytest.mark.asyncio
async def test_knowledge_ingestion_and_semantic_search():
    """Verify knowledge document ingestion and vector search retrieval."""
    async with AsyncSessionLocal() as session:
        # Search for volumetric lighting in knowledge base
        results = await knowledge_retriever.search(
            query="volumetric lighting and camera lenses for cinematic photos",
            session=session,
            top_k=2,
        )
        assert len(results) > 0
        assert "similarity" in results[0]
        assert results[0]["similarity"] > 0.0
        assert "text" in results[0]


@pytest.mark.asyncio
async def test_exact_and_semantic_deduplication():
    """Verify deduplication detects exact text matches and distinct prompts."""
    async with AsyncSessionLocal() as session:
        # 1. Seed a prompt in DB
        p = Prompt(
            title="Cyberpunk Street",
            raw_input="A neon cyberpunk street at midnight with flying cars in the rain",
            user_id="test-user-id",
        )
        session.add(p)
        await session.commit()

        # 2. Exact match check (with different capitalization & whitespace)
        exact_check = await prompt_deduplicator.check_duplicate(
            candidate_text="  a NEON cyberpunk street at midnight with flying cars in the rain!  ",
            session=session,
        )
        assert exact_check["is_duplicate"] is True
        assert exact_check["duplicate_type"] == "EXACT"

        # 3. Unique prompt check
        unique_check = await prompt_deduplicator.check_duplicate(
            candidate_text="How to calculate compound interest in financial forecasting",
            session=session,
        )
        assert unique_check["is_duplicate"] is False
        assert unique_check["duplicate_type"] == "UNIQUE"


@pytest.mark.asyncio
async def test_api_rag_endpoints():
    """Verify POST /api/v1/rag/search and /deduplicate via HTTP."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Search
        search_resp = await client.post(
            "/api/v1/rag/search",
            json={"query": "camera lens depth of field", "top_k": 3},
        )
        assert search_resp.status_code == 200
        results = search_resp.json()["data"]
        assert len(results) > 0

        # 2. Deduplicate
        dedup_resp = await client.post(
            "/api/v1/rag/deduplicate",
            json={"prompt": "A totally novel and unique prompt about astrophysics"},
        )
        assert dedup_resp.status_code == 200
        dedup_data = dedup_resp.json()["data"]
        assert "is_duplicate" in dedup_data
