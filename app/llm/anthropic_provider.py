"""
PromptForge AI - Anthropic Claude Provider Integration.
"""

import time

import httpx

from app.config.constants import ProviderType
from app.config.model_registry import model_registry
from app.config.settings import settings
from app.core.exceptions import ModelProviderException
from app.llm.base import AbstractLLMProvider, LLMResponse


class AnthropicProvider(AbstractLLMProvider):
    """Anthropic Claude API provider implementation via async HTTP."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        if not self.api_key:
            raise ModelProviderException("anthropic", "ANTHROPIC_API_KEY is not configured.", is_retryable=False)

        model_name = model or "claude-3-5-sonnet"
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if stop_sequences:
            payload["stop_sequences"] = stop_sequences

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(f"{self.base_url}/messages", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                raise ModelProviderException("anthropic", f"API status error {e.response.status_code}: {e.response.text}") from e
            except Exception as e:
                raise ModelProviderException("anthropic", f"Network error: {e!s}") from e

        latency = int((time.perf_counter() - start_time) * 1000)

        output_text = data["content"][0]["text"]
        usage = data.get("usage", {})
        in_tokens = usage.get("input_tokens", len(prompt.split()) * 2)
        out_tokens = usage.get("output_tokens", len(output_text.split()) * 2)
        cost = model_registry.estimate_cost(model_name, in_tokens, out_tokens)

        return LLMResponse(
            text=output_text,
            model=model_name,
            provider=ProviderType.ANTHROPIC,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency,
            estimated_cost_usd=cost,
            raw_response=data,
        )

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        # Anthropic does not provide standalone embedding endpoint; fallback to mock
        from app.llm.mock_provider import mock_provider
        return await mock_provider.embed(text, model)


anthropic_provider = AnthropicProvider()
