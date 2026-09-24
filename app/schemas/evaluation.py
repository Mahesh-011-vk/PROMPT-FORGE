"""
PromptForge AI - Evaluation and AI-as-a-Judge Schemas.
"""

from pydantic import BaseModel, Field


class EvaluationMetric(BaseModel):
    """Individual evaluation metric rubric."""

    name: str = Field(..., description="Metric name (e.g. clarity, specificity, constraints)")
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized score from 0 to 100")
    weight: float = Field(default=1.0, description="Relative weight in overall calculation")
    rationale: str = Field(..., description="Reasoning behind this individual score")


class PromptEvaluateRequest(BaseModel):
    """Payload to evaluate prompt quality and adherence."""

    prompt: str = Field(..., description="Prompt text to be evaluated")
    model: str = Field(default="gemini-2.5-flash", description="Target model for execution and evaluation")
    modality: str | None = Field(default=None, description="Modality hint")
    run_llm_judge: bool = Field(default=False, description="If True, runs LLM-as-a-judge completion")


class PromptEvaluateResponse(BaseModel):
    """Comprehensive evaluation report."""

    prompt: str
    overall_score: float = Field(..., description="Overall weighted score (0-100)")
    disclaimer: str = Field(
        default="AI-generated heuristic evaluation based on prompt engineering best practices; not an objective ground truth.",
        description="Responsible AI disclaimer",
    )
    metrics: dict[str, EvaluationMetric]
    latency_ms: int
    tokens_used: int
    estimated_cost_usd: float
    model_evaluated: str
    feedback: list[str]


class ABTestRequest(BaseModel):
    """Payload to compare two prompts head-to-head (A/B testing)."""

    prompt_a: str = Field(..., description="Prompt Variant A")
    prompt_b: str = Field(..., description="Prompt Variant B")
    model: str = Field(default="mock-forge-v1", description="Model to evaluate against")
    criteria: list[str] = Field(default_factory=lambda: ["clarity", "specificity", "constraints", "output_format"])


class ABTestResponse(BaseModel):
    """Head-to-head comparison result."""

    winner: str = Field(..., description="'prompt_a', 'prompt_b', or 'tie'")
    score_a: float
    score_b: float
    rationale: str
    comparison_matrix: dict[str, dict[str, float]]
    latency_ms: int


class BenchmarkSampleResult(BaseModel):
    """Result for one benchmark sample."""

    id: str
    idea: str
    overall_score: float
    latency_ms: int
    tokens: int
    cost: float
    status: str


class BenchmarkReport(BaseModel):
    """Aggregated offline evaluation benchmark report."""

    dataset_name: str
    total_evaluated: int
    average_score: float
    average_latency_ms: float
    total_tokens_used: int
    total_cost_usd: float
    results: list[BenchmarkSampleResult]
