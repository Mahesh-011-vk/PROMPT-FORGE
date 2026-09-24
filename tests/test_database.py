"""
Phase 3 Database Architecture and Model Verification Tests.
Tests async SQLAlchemy models, table creation, relationships, and cascade operations.
"""

import uuid
import pytest
from sqlalchemy import select

from app.config.constants import UserRole
from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.seeder import seed_defaults
from app.models.analytics import UsageEvent
from app.models.evaluation import PromptEvaluation
from app.models.project import Project
from app.models.prompt import Prompt, PromptCategory, PromptTemplate, PromptVersion
from app.models.user import User, UserPreference


@pytest.fixture(autouse=True)
async def setup_test_db():
    """Initializes and seeds database before test execution."""
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_defaults(session)
    yield
    await close_db()


@pytest.mark.asyncio
async def test_database_initialization_and_seeding():
    """Verify that default categories and templates were properly seeded."""
    async with AsyncSessionLocal() as session:
        categories = (await session.execute(select(PromptCategory))).scalars().all()
        assert len(categories) >= 10

        templates = (await session.execute(select(PromptTemplate))).scalars().all()
        assert len(templates) >= 3


@pytest.mark.asyncio
async def test_user_and_preferences_lifecycle():
    """Verify User and UserPreference creation and cascade behavior."""
    unique_email = f"engineer_{uuid.uuid4().hex[:8]}@promptforge.ai"
    async with AsyncSessionLocal() as session:
        user = User(
            email=unique_email,
            hashed_password="hashed_pw_placeholder",
            role=UserRole.POWER_USER,
        )
        pref = UserPreference(
            user=user,
            default_modality="image",
            default_model="gemini-2.5-flash",
            custom_rules={"style": "cinematic"},
        )
        session.add(user)
        session.add(pref)
        await session.commit()
        user_id = user.id

    async with AsyncSessionLocal() as session:
        fetched_user = (
            await session.execute(select(User).where(User.id == user_id))
        ).scalars().first()
        assert fetched_user is not None
        assert fetched_user.email == unique_email
        assert fetched_user.role == UserRole.POWER_USER

        # Cleanup
        await session.delete(fetched_user)
        await session.commit()

    # Verify preference was cascade-deleted
    async with AsyncSessionLocal() as session:
        fetched_pref = (
            await session.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        ).scalars().first()
        assert fetched_pref is None


@pytest.mark.asyncio
async def test_prompt_versioning_and_evaluation_relationships():
    """Verify Prompt, PromptVersion, and PromptEvaluation relational integrity."""
    unique_email = f"architect_{uuid.uuid4().hex[:8]}@promptforge.ai"
    async with AsyncSessionLocal() as session:
        # 1. Create owner
        user = User(
            email=unique_email,
            hashed_password="secure_password_hash",
            role=UserRole.USER,
        )
        session.add(user)
        await session.flush()

        # 2. Create project
        project = Project(
            user_id=user.id,
            name="Cinematic Video Generation",
            description="Campaign video prompts",
        )
        session.add(project)
        await session.flush()

        # 3. Create prompt
        prompt = Prompt(
            user_id=user.id,
            project_id=project.id,
            title="Futuristic Cyberpunk Skyline",
            raw_input="Show a glowing neon city in 2099 with flying vehicles",
            modality="image",
            category="cinematic-image",
            audience="general",
        )
        session.add(prompt)
        await session.flush()

        # 4. Create version 1
        version_1 = PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            prompt_text="A sprawling cyberpunk metropolis at twilight...",
            negative_prompt="blurry, low quality, artifacts",
            structured_spec={"lighting": "neon", "camera": "wide-angle"},
            target_model="midjourney-v6",
            quality_score=88.5,
            change_log="Initial AI generation",
        )
        session.add(version_1)
        await session.flush()

        # 5. Create evaluation
        evaluation = PromptEvaluation(
            prompt_version_id=version_1.id,
            model_name="gemini-2.5-flash",
            overall_score=88.5,
            clarity_score=92.0,
            specificity_score=85.0,
            context_score=90.0,
            constraints_score=87.0,
            safety_score=100.0,
            breakdown={"rule_checks": "all passed"},
            latency_ms=350,
            tokens_used=412,
            estimated_cost=0.0001,
        )
        session.add(evaluation)

        # 6. Log usage event
        event = UsageEvent(
            event_name="prompt_generated",
            user_id=user.id,
            project_id=project.id,
            modality="image",
            category="cinematic-image",
            model_used="gemini-2.5-flash",
            latency_ms=350,
            tokens=412,
            cost=0.0001,
            status="SUCCESS",
        )
        session.add(event)
        await session.commit()

        # Assert IDs generated
        assert prompt.id is not None
        assert version_1.id is not None
        assert evaluation.id is not None
        assert event.id is not None

        # Verify query with joins
        stmt = select(Prompt).where(Prompt.id == prompt.id)
        result = (await session.execute(stmt)).scalars().first()
        assert result.title == "Futuristic Cyberpunk Skyline"
        assert result.modality == "image"
