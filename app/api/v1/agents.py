"""
PromptForge AI - Multi-Agent Orchestration API Endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.agents.critic import CriticAgent
from app.agents.orchestrator import AgentOrchestrator
from app.schemas.agents import (
    AgentOrchestrateRequest,
    AgentOrchestrateResponse,
    StandaloneCritiqueRequest,
    StandaloneCritiqueResponse,
)
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/agents", tags=["Agentic AI & Orchestration"])


@router.post("/orchestrate")
async def orchestrate_agents(
    request: AgentOrchestrateRequest,
) -> ResponseEnvelope[AgentOrchestrateResponse]:
    """Execute autonomous 6-agent pipeline (Planner -> Intent -> Knowledge -> Builder -> Critic -> Safety)."""
    result = await AgentOrchestrator.orchestrate(request)
    return ResponseEnvelope(
        data=result,
        message="Multi-agent prompt synthesis completed successfully",
    )


@router.post("/critique")
async def run_standalone_critique(
    request: StandaloneCritiqueRequest,
) -> ResponseEnvelope[StandaloneCritiqueResponse]:
    """Run CriticAgent audit on any prompt to receive strengths, weaknesses, and suggestions."""
    critique = CriticAgent.evaluate_standalone(
        prompt_text=request.prompt_text,
        modality=request.modality,
        target_model=request.target_model,
    )
    return ResponseEnvelope(data=critique)
