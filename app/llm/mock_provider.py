"""
PromptForge AI - Deterministic Mock LLM Provider.

Provides instant, realistic offline AI completions and 768-dimensional vector embeddings
without external API keys or network latency, specifically engineered for testing and recruiter demos.
"""

import hashlib
import math
import time

from app.config.constants import ProviderType
from app.config.model_registry import model_registry
from app.llm.base import AbstractLLMProvider, LLMResponse


class MockProvider(AbstractLLMProvider):
    """Offline deterministic provider simulating LLM completions and embeddings."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MOCK

    async def is_available(self) -> bool:
        return not self.should_fail

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        """Generates structured simulated response."""
        start_time = time.perf_counter()

        if self.should_fail:
            raise ConnectionError("Mock simulated upstream timeout (503 Service Unavailable).")

        model_name = model or "mock-forge-v1"
        in_tokens = max(10, len(prompt.split()) * 2)
        out_tokens = 150

        # Construct realistic domain completion
        response_text = (
            f"[PromptForge Mock Engine Response for model '{model_name}']\n\n"
            f"Optimized Prompt Specification:\n"
            f"- Objective: Execution of '{prompt[:60]}...'\n"
            f"- Parameters: Temperature={temperature}, MaxTokens={max_tokens}\n"
            f"- Output Strategy: Direct structured execution with strict constraints."
        )

        latency = int((time.perf_counter() - start_time) * 1000) + 15
        cost = model_registry.estimate_cost(model_name, in_tokens, out_tokens)

        return LLMResponse(
            text=response_text,
            model=model_name,
            provider=ProviderType.MOCK,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency,
            estimated_cost_usd=cost,
            finish_reason="stop",
        )

    async def embed(
        self,
        text: str,
        model: str | None = None,
    ) -> list[float]:
        """
        Produces a 768-dimensional deterministic normalized vector using content hashing.
        Allows cosine similarity and semantic search to function correctly in offline mode.
        """
        dimension = 768
        # Create deterministic pseudo-random float vector from text hash
        raw_hash = hashlib.sha256(text.encode("utf-8")).digest()

        vector: list[float] = []
        for i in range(dimension):
            byte_val = raw_hash[i % len(raw_hash)]
            # Map byte (0..255) to float between -1.0 and 1.0 with harmonic frequency
            val = math.sin((i + 1) * (byte_val / 255.0) * math.pi)
            vector.append(val)

        # Normalize to unit length
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [round(x / norm, 6) for x in vector]


mock_provider = MockProvider()
