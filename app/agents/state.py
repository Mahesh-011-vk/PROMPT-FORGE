"""
PromptForge AI - Multi-Agent State Definition.

Defines the shared state container threaded through the multi-agent graph pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas.agents import AgentTraceStep


@dataclass
class AgentState:
    """State blackboard shared and updated by collaborating agents."""

    goal: str
    modality: str = "text"
    persona: str = "Expert AI Specialist"
    audience: str = "adult"
    target_model: str = "gpt-4o"
    include_rag: bool = True
    strict_safety: bool = True

    # Intermediate agent outputs
    plan: dict[str, Any] = field(default_factory=dict)
    intent: dict[str, Any] = field(default_factory=dict)
    knowledge_snippets: list[str] = field(default_factory=list)
    draft_prompt: str = ""
    negative_prompt: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    critique: dict[str, Any] = field(default_factory=dict)
    safety_verdict: str = "APPROVED"
    safety_details: dict[str, Any] = field(default_factory=dict)
    final_prompt: str = ""
    quality_score: float = 0.0

    # Observability & audit trail
    trace: list[AgentTraceStep] = field(default_factory=list)
    total_latency_ms: int = 0
    total_tokens: int = 0

    def add_trace(
        self,
        agent_name: str,
        thought_process: str,
        output_summary: str,
        data: dict[str, Any] | None = None,
        latency_ms: int = 0,
        tokens_used: int = 0,
    ) -> None:
        """Append an execution step to the agent trace."""
        step = AgentTraceStep(
            agent_name=agent_name,
            thought_process=thought_process,
            output_summary=output_summary,
            data=data or {},
            latency_ms=latency_ms,
            tokens_used=tokens_used,
        )
        self.trace.append(step)
        self.total_latency_ms += latency_ms
        self.total_tokens += tokens_used
