"""
SQLAlchemy database models package exports.
"""

from app.models.analytics import AuditLog, UsageEvent
from app.models.base import Base, TimestampMixin, UUIDMixin, generate_uuid, utc_now
from app.models.evaluation import EvaluationRun, PromptEvaluation
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.project import Project
from app.models.prompt import (
    Prompt,
    PromptCategory,
    PromptTemplate,
    PromptVersion,
)
from app.models.user import User, UserPreference

__all__: list[str] = [
    "AuditLog",
    "Base",
    "EvaluationRun",
    "KnowledgeChunk",
    "KnowledgeDocument",
    "Project",
    "Prompt",
    "PromptCategory",
    "PromptEvaluation",
    "PromptTemplate",
    "PromptVersion",
    "TimestampMixin",
    "UUIDMixin",
    "UsageEvent",
    "User",
    "UserPreference",
    "generate_uuid",
    "utc_now",
]
