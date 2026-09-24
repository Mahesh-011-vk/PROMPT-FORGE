"""
PromptForge AI - Google Gemini Provider Integration.
"""

import time

import httpx

from app.config.constants import ProviderType
from app.config.model_registry import model_registry
from app.config.settings import settings
from app.core.exceptions import ModelProviderException
from app.llm.base import AbstractLLMProvider, LLMResponse


class GeminiProvider(AbstractLLMProvider):
    """Google Gemini API provider implementation via async HTTP."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GEMINI

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
            raise ModelProviderException("gemini", "GEMINI_API_KEY is not configured.", is_retryable=False)

        model_name = model or "gemini-2.5-flash"
        endpoint = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System context:\n{system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                raise ModelProviderException("gemini", f"API status error {e.response.status_code}: {e.response.text}") from e
            except Exception as e:
                raise ModelProviderException("gemini", f"Network error: {e!s}") from e

        latency = int((time.perf_counter() - start_time) * 1000)

        # Extract text from response
        try:
            candidates = data.get("candidates", [])
            output_text = candidates[0]["content"]["parts"][0]["text"]
        except (IndexError, KeyError) as e:
            raise ModelProviderException("gemini", "Invalid candidate structure returned from Gemini API.") from e

        usage = data.get("usageMetadata", {})
        in_tokens = usage.get("promptTokenCount", len(prompt.split()) * 2)
        out_tokens = usage.get("candidatesTokenCount", len(output_text.split()) * 2)
        cost = model_registry.estimate_cost(model_name, in_tokens, out_tokens)

        return LLMResponse(
            text=output_text,
            model=model_name,
            provider=ProviderType.GEMINI,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency,
            estimated_cost_usd=cost,
            raw_response=data,
        )

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        """Gemini text-embedding API."""
        if not self.api_key:
            raise ModelProviderException("gemini", "GEMINI_API_KEY is not configured.", is_retryable=False)

        model_name = model or "text-embedding-004"
        endpoint = f"{self.base_url}/models/{model_name}:embedContent?key={self.api_key}"

        payload = {"content": {"parts": [{"text": text}]}}
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(endpoint, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["embedding"]["values"]
            except Exception as e:
                raise ModelProviderException("gemini", f"Embedding failed: {e!s}") from e


gemini_provider = GeminiProvider()
