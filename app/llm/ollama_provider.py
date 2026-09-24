"""
PromptForge AI - Local Ollama Provider Integration.
"""

import time

import httpx

from app.config.constants import ProviderType
from app.config.settings import settings
from app.core.exceptions import ModelProviderException
from app.llm.base import AbstractLLMProvider, LLMResponse


class OllamaProvider(AbstractLLMProvider):
    """Local Ollama instance integration for privacy-first and offline execution."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OLLAMA

    async def is_available(self) -> bool:
        """Checks if local Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/version")
                return res.status_code == 200
        except (httpx.RequestError, Exception):  # noqa: BLE001
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        model_name = model or "llama3.2:latest"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                raise ModelProviderException("ollama", f"Ollama local daemon error: {e!s}") from e

        latency = int((time.perf_counter() - start_time) * 1000)
        output_text = data.get("response", "")
        in_tokens = data.get("prompt_eval_count", len(prompt.split()) * 2)
        out_tokens = data.get("eval_count", len(output_text.split()) * 2)

        return LLMResponse(
            text=output_text,
            model=model_name,
            provider=ProviderType.OLLAMA,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency,
            estimated_cost_usd=0.0,
            raw_response=data,
        )

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        """Ollama local embeddings API."""
        model_name = model or "all-minilm:latest"
        payload = {"model": model_name, "prompt": text}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(f"{self.base_url}/api/embeddings", json=payload)
                res.raise_for_status()
                data = res.json()
                return data["embedding"]
            except Exception as e:
                raise ModelProviderException("ollama", f"Ollama embeddings error: {e!s}") from e


ollama_provider = OllamaProvider()
