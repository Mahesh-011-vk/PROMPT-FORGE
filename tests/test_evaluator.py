"""
Phase 9 Prompt Evaluation Lab, Heuristics, and Benchmark Unit & Integration Tests.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.seeder import seed_defaults
from app.evaluators.heuristics import heuristic_scorer
from app.evaluators.judge import llm_judge
from app.main import app
from app.schemas.evaluation import ABTestRequest
from app.services.evaluator_service import evaluator_service


@pytest.fixture(autouse=True)
async def setup_eval_db():
    """Ensure database is available."""
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_defaults(session)
    yield
    await close_db()


def test_heuristic_quality_scorer_breakdown():
    """Verify heuristic evaluation metrics and scoring rubrics."""
    good_prompt = (
        "You are a Senior Python Architect. Write a production FastAPI service with Pydantic v2 schemas. "
        "Strictly avoid any synchronous I/O. Output in complete, valid Python code."
    )
    score, metrics, _ = heuristic_scorer.evaluate(good_prompt)

    assert score >= 80.0
    assert "clarity" in metrics
    assert "specificity" in metrics
    assert "constraints" in metrics
    assert "output_format" in metrics
    assert "safety" in metrics
    assert metrics["safety"].score == 100.0


@pytest.mark.asyncio
async def test_llm_judge_evaluation():
    """Verify LLM-as-a-judge scoring format and rubrics."""
    prompt = "Create an enterprise prompt for customer support email escalation."
    judge_res = await llm_judge.evaluate_with_judge(prompt, target_model="mock-forge-v1")

    assert "rubrics" in judge_res
    assert judge_res["rubrics"]["relevance"] > 5.0
    assert judge_res["tokens_used"] > 0


@pytest.mark.asyncio
async def test_ab_comparison_evaluator():
    """Verify head-to-head A/B comparison produces a winner and rationale."""
    req = ABTestRequest(
        prompt_a="A cinematic film still of a cybernetic warrior. Shot on 35mm. Detailed lighting. --ar 16:9",
        prompt_b="A cool picture of a warrior.",
    )
    result = await evaluator_service.compare_ab(req)

    assert result.winner == "prompt_a"
    assert result.score_a > result.score_b
    assert "prompt_a" in result.rationale.lower()
    assert "clarity" in result.comparison_matrix


@pytest.mark.asyncio
async def test_offline_benchmark_runner():
    """Verify offline benchmark dataset processing."""
    report = await evaluator_service.run_benchmark(
        dataset_path="datasets/image_prompts.jsonl",
        model="mock-forge-v1",
        max_samples=2,
    )
    assert report.total_evaluated == 2
    assert report.average_score > 0.0
    assert len(report.results) == 2
    assert report.results[0].status == "PASSED"


@pytest.mark.asyncio
async def test_api_evaluation_endpoints():
    """Verify POST /api/v1/prompts/evaluate and /ab-test via HTTP."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Single evaluation
        eval_resp = await client.post(
            "/api/v1/prompts/evaluate",
            json={
                "prompt": "Write a clean REST API in Python using FastAPI with type annotations and pytest tests.",
                "run_llm_judge": False,
            },
        )
        assert eval_resp.status_code == 200
        payload = eval_resp.json()
        assert payload["data"]["overall_score"] > 70.0
        assert "AI-generated heuristic evaluation" in payload["data"]["disclaimer"]

        # 2. A/B test
        ab_resp = await client.post(
            "/api/v1/prompts/ab-test",
            json={
                "prompt_a": "Detailed prompt with explicit constraints and JSON output format.",
                "prompt_b": "good prompt",
            },
        )
        assert ab_resp.status_code == 200
        ab_data = ab_resp.json()["data"]
        assert ab_data["winner"] == "prompt_a"
