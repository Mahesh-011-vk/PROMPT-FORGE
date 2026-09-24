"""
PromptForge AI - Model Capability Registry & Pricing Matrix.

Provides configuration metadata for supported LLM providers and models:
context windows, pricing, modality capabilities, and recommendation heuristics.
"""


from pydantic import BaseModel, Field

from app.config.constants import Modality, ProviderType


class ModelSpec(BaseModel):
    """Specification and capabilities of an individual model."""

    name: str = Field(..., description="Unique model identifier")
    provider: ProviderType = Field(..., description="Provider hosting the model")
    display_name: str = Field(..., description="Human-friendly model title")
    context_window: int = Field(..., description="Maximum token context window")
    supported_modalities: list[Modality] = Field(default_factory=lambda: [Modality.TEXT])
    supports_structured_output: bool = Field(default=True)
    supports_system_prompt: bool = Field(default=True)
    supports_vision: bool = Field(default=False)
    input_cost_per_1m: float = Field(0.0, description="Cost per 1M input tokens in USD")
    output_cost_per_1m: float = Field(0.0, description="Cost per 1M output tokens in USD")
    description: str = Field("", description="Short summary of strengths and best use cases")
    is_active: bool = Field(default=True)


# Default model capabilities registry
DEFAULT_MODEL_REGISTRY: dict[str, ModelSpec] = {
    # Mock / Demo Provider
    "mock-forge-v1": ModelSpec(
        name="mock-forge-v1",
        provider=ProviderType.MOCK,
        display_name="PromptForge Offline Simulator v1",
        context_window=32768,
        supported_modalities=[
            Modality.TEXT,
            Modality.IMAGE,
            Modality.VIDEO,
            Modality.AUDIO,
            Modality.CODE,
            Modality.MULTI_MODAL,
        ],
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_vision=True,
        input_cost_per_1m=0.0,
        output_cost_per_1m=0.0,
        description="Deterministic offline AI simulator for tests and demonstrations without API keys.",
    ),

    # Google Gemini Models
    "gemini-2.5-flash": ModelSpec(
        name="gemini-2.5-flash",
        provider=ProviderType.GEMINI,
        display_name="Google Gemini 2.5 Flash",
        context_window=1048576,
        supported_modalities=[
            Modality.TEXT,
            Modality.IMAGE,
            Modality.VIDEO,
            Modality.AUDIO,
            Modality.CODE,
            Modality.MULTI_MODAL,
        ],
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_vision=True,
        input_cost_per_1m=0.075,
        output_cost_per_1m=0.30,
        description="Fast, low-latency multimodal model with huge context window and native structured outputs.",
    ),
    "gemini-2.5-pro": ModelSpec(
        name="gemini-2.5-pro",
        provider=ProviderType.GEMINI,
        display_name="Google Gemini 2.5 Pro",
        context_window=2097152,
        supported_modalities=[
            Modality.TEXT,
            Modality.IMAGE,
            Modality.VIDEO,
            Modality.AUDIO,
            Modality.CODE,
            Modality.MULTI_MODAL,
        ],
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_vision=True,
        input_cost_per_1m=1.25,
        output_cost_per_1m=5.00,
        description="Flagship multimodal reasoning model for complex prompt architecture and high-fidelity evaluations.",
    ),

    # OpenAI Models
    "gpt-4o": ModelSpec(
        name="gpt-4o",
        provider=ProviderType.OPENAI,
        display_name="OpenAI GPT-4o",
        context_window=128000,
        supported_modalities=[
            Modality.TEXT,
            Modality.IMAGE,
            Modality.CODE,
            Modality.MULTI_MODAL,
        ],
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_vision=True,
        input_cost_per_1m=2.50,
        output_cost_per_1m=10.00,
        description="Omni-model offering high reasoning accuracy, prompt adherence, and structured JSON output.",
    ),
    "gpt-4o-mini": ModelSpec(
        name="gpt-4o-mini",
        provider=ProviderType.OPENAI,
        display_name="OpenAI GPT-4o Mini",
        context_window=128000,
        supported_modalities=[Modality.TEXT, Modality.CODE],
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_vision=True,
        input_cost_per_1m=0.15,
        output_cost_per_1m=0.60,
        description="Cost-efficient and fast model for high-throughput prompt generation and classification.",
    ),

    # Anthropic Claude Models
    "claude-3-5-sonnet": ModelSpec(
        name="claude-3-5-sonnet",
        provider=ProviderType.ANTHROPIC,
        display_name="Anthropic Claude 3.5 Sonnet",
        context_window=200000,
        supported_modalities=[Modality.TEXT, Modality.IMAGE, Modality.CODE],
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_vision=True,
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
        description="Industry benchmark for nuance, complex prompt engineering, and code synthesis.",
    ),

    # Ollama / Local Models
    "llama3.2:latest": ModelSpec(
        name="llama3.2:latest",
        provider=ProviderType.OLLAMA,
        display_name="Meta Llama 3.2 (Local)",
        context_window=131072,
        supported_modalities=[Modality.TEXT, Modality.CODE],
        supports_structured_output=True,
        supports_system_prompt=True,
        supports_vision=False,
        input_cost_per_1m=0.0,
        output_cost_per_1m=0.0,
        description="Locally-hosted open weights model for private and offline execution.",
    ),
}


class ModelRegistry:
    """Registry query and recommendation interface."""

    def __init__(self, registry: dict[str, ModelSpec] | None = None):
        self._registry: dict[str, ModelSpec] = registry or DEFAULT_MODEL_REGISTRY.copy()

    def get(self, model_name: str) -> ModelSpec | None:
        """Fetch specification for a model by name."""
        return self._registry.get(model_name)

    def list_all(
        self,
        provider: ProviderType | None = None,
        modality: Modality | None = None,
    ) -> list[ModelSpec]:
        """List active models optionally filtered by provider and modality."""
        models = [m for m in self._registry.values() if m.is_active]
        if provider:
            models = [m for m in models if m.provider == provider]
        if modality:
            models = [m for m in models if modality in m.supported_modalities]
        return models

    def estimate_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculates estimated cost in USD based on model pricing matrix.
        Returns 0.0 if model is unknown or free.
        """
        spec = self.get(model_name)
        if not spec:
            return 0.0

        input_cost = (input_tokens / 1_000_000) * spec.input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * spec.output_cost_per_1m
        return round(input_cost + output_cost, 6)

    def recommend_model(
        self,
        modality: Modality,
        requires_vision: bool = False,
        prefer_local: bool = False,
    ) -> ModelSpec:
        """
        Recommends the optimal model based on modality, constraints, and provider availability.
        """
        if prefer_local:
            for spec in self._registry.values():
                if spec.provider == ProviderType.OLLAMA and spec.is_active:
                    return spec

        # Filter by modality and vision requirement
        candidates = [
            m for m in self._registry.values()
            if m.is_active and modality in m.supported_modalities
        ]
        if requires_vision:
            candidates = [m for m in candidates if m.supports_vision]

        if not candidates:
            return self._registry["mock-forge-v1"]

        # Default preference order: Gemini 2.5 Flash -> GPT-4o -> Mock
        for preferred in ("gemini-2.5-flash", "gpt-4o", "mock-forge-v1"):
            for cand in candidates:
                if cand.name == preferred:
                    return cand

        return candidates[0]


model_registry = ModelRegistry()
