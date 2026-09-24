"""
PromptForge AI - Database Seeder.

Seeds initial taxonomy categories, system templates, and reference knowledge.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.prompt import PromptCategory, PromptTemplate

SEED_CATEGORIES = [
    # Text
    {"name": "General Writing", "slug": "general-writing", "modality": "text", "description": "Standard prose and text composition."},
    {"name": "Creative Writing", "slug": "creative-writing", "modality": "text", "description": "Narrative, fiction, storytelling, and scripts."},
    {"name": "Summarization", "slug": "summarization", "modality": "text", "description": "Condensing documents and key takeaway extraction."},
    {"name": "Productivity", "slug": "productivity", "modality": "text", "description": "Time management, planning, and task structuring."},
    # Business
    {"name": "Business Strategy", "slug": "business-strategy", "modality": "text", "description": "Market analysis, competitive research, and strategic plans."},
    {"name": "Marketing & Copywriting", "slug": "marketing-copywriting", "modality": "text", "description": "Campaign copy, value propositions, and ads."},
    {"name": "Customer Support", "slug": "customer-support", "modality": "text", "description": "Support macros, empathetic replies, and ticket triage."},
    # Developer
    {"name": "Software Development", "slug": "software-development", "modality": "code", "description": "Application architecture, clean code, and API design."},
    {"name": "Python Engineering", "slug": "python-engineering", "modality": "code", "description": "FastAPI, async programming, data pipelines, and algorithms."},
    {"name": "Debugging & Refactoring", "slug": "debugging-refactoring", "modality": "code", "description": "Error remediation, performance optimization, and linting."},
    {"name": "Machine Learning & MLOps", "slug": "machine-learning-mlops", "modality": "code", "description": "Model training, evaluation, and pipeline orchestration."},
    # Image
    {"name": "Cinematic Image", "slug": "cinematic-image", "modality": "image", "description": "Dramatic lighting, film stills, volumetric atmosphere."},
    {"name": "Photorealistic", "slug": "photorealistic", "modality": "image", "description": "True-to-life studio photography, accurate textures and lenses."},
    {"name": "Concept Art", "slug": "concept-art", "modality": "image", "description": "World-building, environment concepts, character design."},
    {"name": "3D & Renders", "slug": "3d-renders", "modality": "image", "description": "Octane render, Unreal Engine 5, ray tracing aesthetic."},
    # Video
    {"name": "Cinematic Video", "slug": "cinematic-video", "modality": "video", "description": "Scene-by-scene tracking shots, pacing, and motion cues."},
    {"name": "Product Advertisement", "slug": "product-advertisement", "modality": "video", "description": "Dynamic commercial spot, product reveals, smooth pans."},
    # Audio
    {"name": "Podcast & Voiceover", "slug": "podcast-voiceover", "modality": "audio", "description": "Spoken word cadence, pacing, microphone proximity, and tone."},
    # Education
    {"name": "STEM & Mathematics", "slug": "stem-mathematics", "modality": "text", "description": "Step-by-step proofs, conceptual analogies, and math breakdowns."},
    {"name": "Kids Educational", "slug": "kids-educational", "modality": "text", "description": "Child-safe, engaging, gamified learning stories."},
]

SEED_TEMPLATES = [
    {
        "title": "Cinematic Image Master",
        "description": "Produces a rich, photorealistic, cinematic prompt with camera, lens, and lighting tags.",
        "modality": "image",
        "category": "cinematic-image",
        "template_str": (
            "A cinematic film still of {{subject}}, {{environment}}. "
            "Shot on {{camera}} with {{lens}} lens. Lighting: {{lighting}}, {{mood}} atmosphere. "
            "Color grade: {{color_palette}}. Hyper-detailed textures, 8k resolution, photorealistic."
        ),
        "default_variables": {
            "subject": "a lone astronaut walking",
            "environment": "on an alien obsidian desert under twin moons",
            "camera": "ARRI Alexa 65",
            "lens": "35mm anamorphic",
            "lighting": "dramatic rim lighting and bioluminescent glow",
            "mood": "mysterious and awe-inspiring",
            "color_palette": "deep teal, amber, and obsidian black",
        },
        "is_system": True,
    },
    {
        "title": "Production Python Async Service",
        "description": "Prompt for generating production-ready asynchronous Python code with typing and tests.",
        "modality": "code",
        "category": "python-engineering",
        "template_str": (
            "You are a Principal Python Software Engineer. Write a production-grade, asynchronous implementation of: "
            "{{requirement}} using {{framework}}.\n\n"
            "Requirements:\n"
            "1. Strict type hinting with Pydantic v2 schemas.\n"
            "2. Clean error handling with custom domain exceptions.\n"
            "3. Structured logging with context.\n"
            "4. Asynchronous I/O using asyncio.\n"
            "5. Unit tests using pytest and pytest-asyncio."
        ),
        "default_variables": {
            "requirement": "a Redis-backed token bucket rate limiter middleware",
            "framework": "FastAPI",
        },
        "is_system": True,
    },
    {
        "title": "Child-Safe Educational Story",
        "description": "Engaging, gentle, and child-safe educational story with simple vocabulary.",
        "modality": "text",
        "category": "kids-educational",
        "template_str": (
            "Write a warm, gentle, and imaginative educational story for a {{age_group}} child about {{topic}}. "
            "Make it exciting and easy to understand. Keep sentences short and vocabulary age-appropriate. "
            "Include a kind character named {{character}} who discovers how {{learning_goal}} works."
        ),
        "default_variables": {
            "age_group": "7-year-old",
            "topic": "why leaves change color in autumn",
            "character": "Barnaby the curious squirrel",
            "learning_goal": "trees save energy for winter by absorbing green chlorophyll",
        },
        "is_system": True,
    },
]


async def seed_defaults(session: AsyncSession) -> None:
    """Seeds default categories and templates if not already present."""
    logger.info("Checking database seed status...")

    # Seed Categories
    cat_query = await session.execute(select(PromptCategory.id).limit(1))
    if not cat_query.scalars().first():
        logger.info("Seeding initial prompt taxonomy categories...")
        for cat_data in SEED_CATEGORIES:
            cat = PromptCategory(**cat_data)
            session.add(cat)
        await session.commit()
        logger.info(f"Seeded {len(SEED_CATEGORIES)} categories.")

    # Seed Templates
    tmpl_query = await session.execute(select(PromptTemplate.id).limit(1))
    if not tmpl_query.scalars().first():
        logger.info("Seeding initial prompt templates...")
        for tmpl_data in SEED_TEMPLATES:
            tmpl = PromptTemplate(**tmpl_data)
            session.add(tmpl)
        await session.commit()
        logger.info(f"Seeded {len(SEED_TEMPLATES)} system templates.")
