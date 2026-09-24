"""
PromptForge AI - Knowledge Agent.

Retrieves domain best practices and prompt engineering patterns from RAG vector store.
"""

from __future__ import annotations

import time

from app.agents.state import AgentState
from app.rag.retriever import KnowledgeRetriever


class KnowledgeAgent:
    """Queries vector knowledge retriever for contextual prompting strategies."""

    NAME = "KnowledgeAgent"

    @classmethod
    async def run(cls, state: AgentState) -> None:
        """Query knowledge base for prompting patterns matching goal and modality."""
        start = time.perf_counter()

        snippets: list[str] = []
        if state.include_rag:
            retriever = KnowledgeRetriever()
            query = f"{state.modality} prompt engineering best practices {state.goal}"
            matches = await retriever.search(query=query, top_k=2, min_similarity=-1.0)
            snippets = [m.get("text", "") for m in matches if isinstance(m, dict)]

        if not snippets:
            # Fallback domain knowledge
            if state.modality == "image":
                snippets.append(
                    "Include subject details, lighting environment (e.g. volumetric lighting), "
                    "camera lens specification (e.g. 85mm f/1.4), composition framing, and rendering engine."
                )
            elif state.modality == "video":
                snippets.append(
                    "Specify camera motion trajectory (slow pan, dolly-in, crane shot), frame rate, lighting transitions, and temporal progression."
                )
            elif state.modality == "code":
                snippets.append(
                    "Specify typing, error handling, edge cases, test coverage, and require chain-of-thought code reasoning."
                )
            else:
                snippets.append(
                    "Use clear role definition, delimiters for context, explicit constraint checklists, and few-shot formatting."
                )

        state.knowledge_snippets = snippets

        latency = int((time.perf_counter() - start) * 1000)
        state.add_trace(
            agent_name=cls.NAME,
            thought_process=f"Retrieved {len(snippets)} prompting knowledge anchors for modality '{state.modality}'.",
            output_summary=f"Extracted {len(snippets)} engineering guidelines.",
            data={"snippets_count": len(snippets)},
            latency_ms=max(latency, 2),
            tokens_used=120,
        )
