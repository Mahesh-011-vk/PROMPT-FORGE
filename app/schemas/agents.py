"""
PromptForge AI - Multi-Agent Orchestration Schemas.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentTraceStep(BaseModel):
    """Execution audit record for a single agent node."""

    agent_name: str
    status: str = "COMPLETED"
    thought_process: str
    output_summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0
    tokens_used: int = 0


class AgentOrchestrateRequest(BaseModel):
    """Payload to initiate autonomous multi-agent prompt construction."""

    goal: str = Field(
        ...,
        min_length=3,
        description="The high-level prompt objective or raw task description",
        json_schema_extra={"example": "Generate a production prompt for an AI code reviewer checking Python async safety"},
    )
    modality: str | None = Field(None, description="Optional forced modality (text, image, video, code)")
    persona: str | None = Field(None, description="Target persona (e.g., Staff Software Engineer)")
    audience: str | None = Field("adult", description="Target audience: adult, kids, or general")
    target_model: str | None = Field("gpt-4o", description="Target model deployment")
    include_rag_knowledge: bool = Field(True, description="Whether to query RAG vector knowledge base")
    strict_safety: bool = Field(True, description="Run safety and alignment verification")


class StandaloneCritiqueRequest(BaseModel):
    """Payload to critique an existing prompt."""

    prompt_text: str = Field(..., min_length=5)
    modality: str = Field("text")
    target_model: str = Field("gpt-4o")


class StandaloneCritiqueResponse(BaseModel):
    """Detailed critique analysis from the CriticAgent."""

    overall_verdict: str
    quality_score: float
    strengths: list[str]
    weaknesses: list[str]
    suggested_improvements: list[str]
    ambiguity_flags: list[str]


class AgentOrchestrateResponse(BaseModel):
    """Final output artifact from the multi-agent pipeline."""

    final_prompt: str
    negative_prompt: str | None = None
    structured_spec: dict[str, Any] = Field(default_factory=dict)
    variables: dict[str, Any] = Field(default_factory=dict)
    quality_score: float
    critique_summary: list[str] = Field(default_factory=list)
    safety_verdict: str
    agent_trace: list[AgentTraceStep] = Field(default_factory=list)
    total_latency_ms: int = 0
    total_tokens: int = 0
