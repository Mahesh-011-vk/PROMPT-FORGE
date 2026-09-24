"""
PromptForge AI - Semantic & Exact Prompt Deduplication Engine.

Detects exact text matches and near-duplicate semantic variants using normalized hashes
and dense embedding cosine similarity.
"""

import hashlib
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.router import model_router
from app.models.prompt import Prompt
from app.rag.retriever import cosine_similarity


class PromptDeduplicator:
    """Detects exact and semantic duplicates to prevent prompt library clutter."""

    def normalize(self, text: str) -> str:
        """Normalizes punctuation and whitespace for exact-match comparisons."""
        lower = text.lower()
        # Remove punctuation and normalize whitespace
        cleaned = re.sub(r"[^\w\s]", "", lower)
        return re.sub(r"\s+", " ", cleaned).strip()

    def compute_hash(self, text: str) -> str:
        """Computes deterministic MD5 digest of normalized text."""
        return hashlib.md5(self.normalize(text).encode("utf-8")).hexdigest()

    async def check_duplicate(
        self,
        candidate_text: str,
        session: AsyncSession,
        similarity_threshold: float = 0.92,
    ) -> dict:
        """
        Scans saved prompts in database to detect exact or semantic duplicates.
        """
        norm_candidate = self.normalize(candidate_text)
        cand_hash = self.compute_hash(candidate_text)

        # 1. Exact match check
        prompts = (await session.execute(select(Prompt))).scalars().all()
        for p in prompts:
            if self.compute_hash(p.raw_input) == cand_hash:
                return {
                    "is_duplicate": True,
                    "duplicate_type": "EXACT",
                    "matched_prompt_id": p.id,
                    "matched_title": p.title,
                    "similarity": 1.0,
                }

        # 2. Semantic vector similarity check
        cand_vector = await model_router.embed(candidate_text)
        best_match_id = None
        best_match_title = None
        highest_similarity = 0.0

        for p in prompts:
            prompt_vector = await model_router.embed(p.raw_input)
            sim = cosine_similarity(cand_vector, prompt_vector)
            if sim > highest_similarity:
                highest_similarity = sim
                best_match_id = p.id
                best_match_title = p.title

        if highest_similarity >= similarity_threshold:
            return {
                "is_duplicate": True,
                "duplicate_type": "SEMANTIC_NEAR_DUPLICATE",
                "matched_prompt_id": best_match_id,
                "matched_title": best_match_title,
                "similarity": round(highest_similarity, 4),
            }

        return {
            "is_duplicate": False,
            "duplicate_type": "UNIQUE",
            "matched_prompt_id": None,
            "similarity": round(highest_similarity, 4),
        }


prompt_deduplicator = PromptDeduplicator()
