"""
Application configuration management for PromptForge AI.
"""


from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import Environment, ProviderType, UserRole


class RateLimitConfig(BaseModel):
    """Rate limit configurations per user role (requests per minute)."""

    ANONYMOUS: int = 15
    USER: int = 60
    POWER_USER: int = 300
    ADMIN: int = 1200


class Settings(BaseSettings):
    """Global application settings with environment variable override and validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    APP_NAME: str = "PromptForge AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    DEMO_MODE: bool = True  # When True, fallback to simulated offline responses

    # Server & API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)
    SECRET_KEY: str = "promptforge-super-secret-key-change-in-production-32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON_FORMAT: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./promptforge.db"
    POSTGRES_URL: str | None = None
    ECHO_SQL: bool = False

    # Redis Cache & Task Queue
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_IN_MEMORY_CACHE: bool = True

    # AI Provider API Keys
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_PROVIDER: ProviderType = ProviderType.MOCK

    # Vector DB & Embeddings
    VECTOR_DB_TYPE: str = "memory"  # 'memory' or 'pgvector'
    EMBEDDING_DIMENSION: int = 768

    # Rate Limiting
    RATE_LIMITS: RateLimitConfig = Field(default_factory=RateLimitConfig)

    # Feature Flags
    ENABLE_RAG: bool = True
    ENABLE_AGENTS: bool = True
    ENABLE_ANALYTICS: bool = True
    ENABLE_EVALUATION: bool = True
    ENABLE_PROMPT_INJECTION_DEFENSE: bool = True

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return upper_v

    @property
    def is_sqlite(self) -> bool:
        """Returns True if the active database is SQLite."""
        return "sqlite" in self.DATABASE_URL.lower()

    @property
    def active_providers(self) -> list[ProviderType]:
        """Returns the list of currently configured and operational providers."""
        providers: list[ProviderType] = [ProviderType.MOCK]
        if self.GEMINI_API_KEY:
            providers.append(ProviderType.GEMINI)
        if self.OPENAI_API_KEY:
            providers.append(ProviderType.OPENAI)
        if self.ANTHROPIC_API_KEY:
            providers.append(ProviderType.ANTHROPIC)
        # Ollama is always reachable if local service is up
        providers.append(ProviderType.OLLAMA)
        return providers

    def get_rate_limit_for_role(self, role: UserRole) -> int:
        """Returns requests per minute allowed for a specific role."""
        if role == UserRole.ADMIN:
            return self.RATE_LIMITS.ADMIN
        elif role == UserRole.POWER_USER:
            return self.RATE_LIMITS.POWER_USER
        elif role == UserRole.USER:
            return self.RATE_LIMITS.USER
        return self.RATE_LIMITS.ANONYMOUS


settings = Settings()
