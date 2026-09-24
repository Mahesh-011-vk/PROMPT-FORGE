"""
PromptForge AI - Application Constants.
"""

from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CODE = "code"
    AGENT = "agent"
    RESEARCH = "research"
    DATA = "data"
    MULTI_MODAL = "multi-modal"


class AudienceCategory(str, Enum):
    KIDS = "kids"
    TEENAGERS = "teenagers"
    ADULTS = "adults"
    PROFESSIONALS = "professionals"
    DEVELOPERS = "developers"
    RESEARCHERS = "researchers"
    BEGINNERS = "beginners"
    EXPERTS = "experts"


class SafetyClassification(str, Enum):
    SAFE = "SAFE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    DISALLOWED = "DISALLOWED"


class UserRole(str, Enum):
    USER = "USER"
    POWER_USER = "POWER_USER"
    ADMIN = "ADMIN"


class ProviderType(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    MOCK = "mock"
