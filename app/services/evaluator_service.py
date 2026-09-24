"""
PromptForge AI - Evaluation Lab & Benchmark Service.

Orchestrates heuristic evaluations, LLM-as-a-judge assessments, A/B prompt comparisons,
and offline benchmark dataset executions.
"""

import json
import os
import time

import aiofiles

from app.evaluators.heuristics import heuristic_scorer
from app.evaluators.judge import llm_judge
from app.schemas.evaluation import (
    ABTestRequest,
    ABTestResponse,
    BenchmarkReport,
    BenchmarkSampleResult,
    PromptEvaluateRequest,
    PromptEvaluateResponse,
)


class EvaluatorService:
    """Prompt Testing Lab and Evaluation Service."""

    async def evaluate(self, request: PromptEvaluateRequest) -> PromptEvaluateResponse:
        """Runs multi-metric heuristic evaluation and optional LLM judge."""
        start_time = time.perf_counter()
        score, metrics, feedback = heuristic_scorer.evaluate(request.prompt, modality=request.modality or "text")

        tokens_used = len(request.prompt.split()) * 2
        cost = 0.0

        if request.run_llm_judge:
            judge_res = await llm_judge.evaluate_with_judge(request.prompt, target_model=request.model)
            tokens_used += judge_res["tokens_used"]
            cost += judge_res["estimated_cost_usd"]

        latency = int((time.perf_counter() - start_time) * 1000)

        return PromptEvaluateResponse(
            prompt=request.prompt,
            overall_score=score,
            metrics=metrics,
            latency_ms=latency,
            tokens_used=tokens_used,
            estimated_cost_usd=cost,
            model_evaluated=request.model,
            feedback=feedback,
        )

    async def compare_ab(self, request: ABTestRequest) -> ABTestResponse:
        """Executes head-to-head comparative evaluation between Prompt A and Prompt B."""
        start_time = time.perf_counter()

        score_a, metrics_a, _ = heuristic_scorer.evaluate(request.prompt_a)
        score_b, metrics_b, _ = heuristic_scorer.evaluate(request.prompt_b)

        comparison_matrix: dict[str, dict[str, float]] = {}
        for criterion in request.criteria:
            val_a = metrics_a.get(criterion, metrics_a["clarity"]).score
            val_b = metrics_b.get(criterion, metrics_b["clarity"]).score
            comparison_matrix[criterion] = {"prompt_a": val_a, "prompt_b": val_b}

        if score_a > score_b + 2.0:
            winner = "prompt_a"
            rationale = f"Prompt Variant A (prompt_a) scored higher ({score_a} vs {score_b}) due to superior constraint and format specificity."
        elif score_b > score_a + 2.0:
            winner = "prompt_b"
            rationale = f"Prompt Variant B (prompt_b) scored higher ({score_b} vs {score_a}) due to greater contextual depth and explicit parameters."
        else:
            winner = "tie"
            rationale = f"Both variants demonstrated comparable quality ({score_a} vs {score_b})."

        latency = int((time.perf_counter() - start_time) * 1000)

        return ABTestResponse(
            winner=winner,
            score_a=score_a,
            score_b=score_b,
            rationale=rationale,
            comparison_matrix=comparison_matrix,
            latency_ms=latency,
        )

    async def run_benchmark(self, dataset_path: str, model: str = "mock-forge-v1", max_samples: int = 10) -> BenchmarkReport:
        """Runs offline benchmark dataset evaluation (.jsonl)."""
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Benchmark dataset '{dataset_path}' not found.")

        samples = []
        async with aiofiles.open(dataset_path, mode="r", encoding="utf-8") as f:
            async for line in f:
                if line.strip():
                    samples.append(json.loads(line))
                if len(samples) >= max_samples:
                    break

        results: list[BenchmarkSampleResult] = []
        total_score = 0.0
        total_latency = 0
        total_tokens = 0
        total_cost = 0.0

        for sample in samples:
            sample_id = sample.get("id", "sample")
            idea = sample.get("idea", "")
            modality = sample.get("modality", "text")

            start = time.perf_counter()
            score, _, _ = heuristic_scorer.evaluate(idea, modality=modality)
            lat = int((time.perf_counter() - start) * 1000) + 10
            tokens = len(idea.split()) * 3
            cost = 0.00001

            total_score += score
            total_latency += lat
            total_tokens += tokens
            total_cost += cost

            results.append(
                BenchmarkSampleResult(
                    id=sample_id,
                    idea=idea,
                    overall_score=score,
                    latency_ms=lat,
                    tokens=tokens,
                    cost=cost,
                    status="PASSED" if score >= 50.0 else "NEEDS_REVIEW",
                )
            )

        n = len(results) or 1
        return BenchmarkReport(
            dataset_name=os.path.basename(dataset_path),
            total_evaluated=len(results),
            average_score=round(total_score / n, 2),
            average_latency_ms=round(total_latency / n, 2),
            total_tokens_used=total_tokens,
            total_cost_usd=round(total_cost, 6),
            results=results,
        )


evaluator_service = EvaluatorService()
