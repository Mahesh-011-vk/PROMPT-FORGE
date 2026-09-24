"""
PromptForge AI - OpenAI Provider Integration.
"""

import time

import httpx

from app.config.constants import ProviderType
from app.config.model_registry import model_registry
from app.config.settings import settings
from app.core.exceptions import ModelProviderException
from app.llm.base import AbstractLLMProvider, LLMResponse


class OpenAIProvider(AbstractLLMProvider):
    """OpenAI API provider implementation via async HTTP."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI

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
            raise ModelProviderException("openai", "OPENAI_API_KEY is not configured.", is_retryable=False)

        model_name = model or "gpt-4o-mini"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if stop_sequences:
            payload["stop"] = stop_sequences

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                raise ModelProviderException("openai", f"API status error {e.response.status_code}: {e.response.text}") from e
            except Exception as e:
                raise ModelProviderException("openai", f"Network error: {e!s}") from e

        latency = int((time.perf_counter() - start_time) * 1000)

        output_text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        in_tokens = usage.get("prompt_tokens", len(prompt.split()) * 2)
        out_tokens = usage.get("completion_tokens", len(output_text.split()) * 2)
        cost = model_registry.estimate_cost(model_name, in_tokens, out_tokens)

        return LLMResponse(
            text=output_text,
            model=model_name,
            provider=ProviderType.OPENAI,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency,
            estimated_cost_usd=cost,
            finish_reason=data["choices"][0].get("finish_reason", "stop"),
            raw_response=data,
        )

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        """OpenAI text-embedding-3-small API."""
        if not self.api_key:
            raise ModelProviderException("openai", "OPENAI_API_KEY is not configured.", is_retryable=False)

        model_name = model or "text-embedding-3-small"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"input": text, "model": model_name}

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(f"{self.base_url}/embeddings", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["data"][0]["embedding"]
            except Exception as e:
                raise ModelProviderException("openai", f"Embedding failed: {e!s}") from e


openai_provider = OpenAIProvider()
