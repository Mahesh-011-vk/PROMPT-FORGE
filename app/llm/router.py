"""
PromptForge AI - Multi-Model Router & Circuit Breaker.

Provides vendor-independent model execution, intelligent routing, and automated fallback failover.
"""


from app.config.constants import ProviderType
from app.config.model_registry import model_registry
from app.config.settings import settings
from app.core.logging import logger
from app.llm.anthropic_provider import anthropic_provider
from app.llm.base import AbstractLLMProvider, LLMResponse
from app.llm.gemini_provider import gemini_provider
from app.llm.mock_provider import mock_provider
from app.llm.ollama_provider import ollama_provider
from app.llm.openai_provider import openai_provider


class ModelRouter:
    """Manages provider dispatch, availability checks, and circuit-breaker fallbacks."""

    def __init__(self):
        self._providers: dict[ProviderType, AbstractLLMProvider] = {
            ProviderType.MOCK: mock_provider,
            ProviderType.GEMINI: gemini_provider,
            ProviderType.OPENAI: openai_provider,
            ProviderType.ANTHROPIC: anthropic_provider,
            ProviderType.OLLAMA: ollama_provider,
        }

    def get_provider(self, provider: ProviderType | str) -> AbstractLLMProvider:
        """Resolves an active provider instance by type or string identifier."""
        if isinstance(provider, str):
            try:
                p_type = ProviderType(provider.lower())
            except ValueError:
                p_type = ProviderType.MOCK
        else:
            p_type = provider

        return self._providers.get(p_type, mock_provider)

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        preferred_provider: ProviderType | str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        allow_fallback: bool = True,
    ) -> LLMResponse:
        """
        Executes generation against preferred provider with automated circuit-breaker failover.
        """
        model_name = model or "mock-forge-v1"

        # Determine primary provider from model spec or argument
        if preferred_provider:
            primary_provider = self.get_provider(preferred_provider)
        else:
            spec = model_registry.get(model_name)
            if spec:
                primary_provider = self.get_provider(spec.provider)
            else:
                primary_provider = self.get_provider(settings.DEFAULT_PROVIDER)

        fallback_activated = False
        if not await primary_provider.is_available():
            logger.info(f"Provider '{primary_provider.provider_type.value}' is unavailable; activating fallback to Mock Provider.")
            primary_provider = self._providers[ProviderType.MOCK]
            model_name = "mock-forge-v1"
            fallback_activated = True

        try:
            resp = await primary_provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            resp.fallback_used = fallback_activated
            return resp
        except Exception as exc:
            if not allow_fallback or primary_provider.provider_type == ProviderType.MOCK:
                raise

            logger.warning(
                f"Primary provider '{primary_provider.provider_type.value}' failed ({exc!s}). "
                f"Activating circuit-breaker fallback to Mock Provider."
            )
            fallback_response = await self._providers[ProviderType.MOCK].generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model="mock-forge-v1",
                temperature=temperature,
                max_tokens=max_tokens,
            )
            fallback_response.fallback_used = True
            return fallback_response

    async def embed(self, text: str, preferred_provider: ProviderType | str | None = None) -> list[float]:
        """Routes vector embedding request to active embedding provider."""
        provider = self.get_provider(preferred_provider or ProviderType.MOCK)
        if not await provider.is_available():
            provider = mock_provider
        return await provider.embed(text)


model_router = ModelRouter()
