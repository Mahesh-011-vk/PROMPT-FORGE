"""
PromptForge AI - Multi-Agent Graph Orchestrator.

Orchestrates sequential and conditional execution of the specialized prompt engineering agents.
"""

from __future__ import annotations

import time

from app.agents.builder import BuilderAgent
from app.agents.critic import CriticAgent
from app.agents.intent import IntentAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.planner import PlannerAgent
from app.agents.safety import SafetyAgent
from app.agents.state import AgentState
from app.schemas.agents import AgentOrchestrateRequest, AgentOrchestrateResponse


class AgentOrchestrator:
    """Master orchestrator executing the collaborative multi-agent pipeline."""

    @classmethod
    async def orchestrate(cls, request: AgentOrchestrateRequest) -> AgentOrchestrateResponse:
        """Run the full multi-agent prompt synthesis workflow."""
        start_time = time.perf_counter()

        # Initialize shared blackboard state
        state = AgentState(
            goal=request.goal,
            modality=request.modality or "text",
            persona=request.persona or "Expert AI Specialist",
            audience=request.audience or "adult",
            target_model=request.target_model or "gpt-4o",
            include_rag=request.include_rag_knowledge,
            strict_safety=request.strict_safety,
        )

        # 1. Planner Agent
        await PlannerAgent.run(state)

        # 2. Intent Agent
        await IntentAgent.run(state)

        # 3. Knowledge Agent (RAG retrieval)
        await KnowledgeAgent.run(state)

        # 4. Builder Agent (Draft generation)
        await BuilderAgent.run(state)

        # 5. Critic Agent (Adversarial evaluation & scoring)
        await CriticAgent.run(state)

        # 6. Safety Agent (Alignment & guardrails check)
        await SafetyAgent.run(state)

        # 7. Finalizer Node
        if state.safety_verdict == "BLOCKED":
            state.final_prompt = (
                "[PROMPT GENERATION BLOCKED BY SAFETY GUARDRAIL]\n"
                "The input request contained safety violations or adversarial injection patterns that violate system policy."
            )
            state.negative_prompt = None
            state.quality_score = 0.0
        else:
            state.final_prompt = state.draft_prompt

        total_latency = int((time.perf_counter() - start_time) * 1000)

        # Extract critique highlights
        critique_summary = (
            state.critique.get("strengths", [])[:2] + state.critique.get("suggestions", [])[:2]
            if state.critique
            else []
        )

        return AgentOrchestrateResponse(
            final_prompt=state.final_prompt,
            negative_prompt=state.negative_prompt,
            structured_spec=state.intent,
            variables=state.variables,
            quality_score=state.quality_score,
            critique_summary=critique_summary,
            safety_verdict=state.safety_verdict,
            agent_trace=state.trace,
            total_latency_ms=total_latency,
            total_tokens=state.total_tokens,
        )
