"""
PromptForge AI - Taxonomy & Modality Detection Engine.

Provides category classification, modality detection heuristics, and audience profiling.
"""

import re

from app.config.constants import AudienceCategory, Modality

# Modality keyword indicators
MODALITY_KEYWORDS: dict[Modality, list[str]] = {
    Modality.IMAGE: [
        "image", "photo", "photography", "photorealistic", "portrait", "landscape",
        "cinematic", "wallpaper", "illustration", "drawing", "render", "3d render",
        "anime", "logo", "poster", "midjourney", "stable diffusion", "flux", "artwork",
        "painting", "concept art", "visual", "shot on",
    ],
    Modality.VIDEO: [
        "video", "animation", "motion", "cinematic video", "scene", "clip", "footage",
        "camera movement", "tracking shot", "drone shot", "sora", "runway", "kling",
        "panning", "slow motion", "commercial", "short film", "reel", "youtube video",
        "youtube", "advertisement", "ad", "promo",
    ],
    Modality.AUDIO: [
        "audio", "voice", "podcast", "music", "sound effect", "narration", "voiceover",
        "speech", "melody", "soundtrack", "vocal", "instrumental", "ambient sound",
    ],
    Modality.CODE: [
        "code", "function", "class", "script", "algorithm", "python", "javascript",
        "typescript", "sql", "api", "fastapi", "django", "react", "bug", "debug",
        "refactor", "unit test", "database", "backend", "dockerfile", "endpoint",
    ],
    Modality.AGENT: [
        "agent", "autonomous", "tool use", "function calling", "multi-agent",
        "reasoning loop", "planner", "subagent", "supervisor", "workflow",
    ],
    Modality.RESEARCH: [
        "research", "paper", "literature review", "citation", "academic", "scientific",
        "hypothesis", "meta-analysis", "arxiv", "methodology", "dissertation",
    ],
    Modality.DATA: [
        "data", "dataset", "dataframe", "pandas", "sql query", "etl", "pipeline",
        "analytics", "aggregation", "visualization", "chart", "metrics",
    ],
}

# Audience keywords
AUDIENCE_KEYWORDS: dict[AudienceCategory, list[str]] = {
    AudienceCategory.KIDS: [
        "child", "children", "kid", "kids", "toddler", "grade school", "elementary",
        "bedtime story", "cartoon", "fairy tale", "fun learning", "simple words",
    ],
    AudienceCategory.TEENAGERS: [
        "teen", "teenager", "high school", "youth", "gen z",
    ],
    AudienceCategory.DEVELOPERS: [
        "developer", "programmer", "engineer", "dev", "coder", "technical team",
    ],
    AudienceCategory.RESEARCHERS: [
        "researcher", "scientist", "scholar", "academic", "phd", "postdoc",
    ],
    AudienceCategory.PROFESSIONALS: [
        "executive", "manager", "client", "stakeholder", "enterprise", "business",
        "corporate", "professional", "investor",
    ],
    AudienceCategory.BEGINNERS: [
        "beginner", "novice", "explain simply", "for dummies", "101", "introductory",
    ],
    AudienceCategory.EXPERTS: [
        "expert", "senior", "advanced", "in-depth", "rigorous", "deep dive",
    ],
}


def detect_modality(text: str, default: Modality = Modality.TEXT) -> Modality:
    """
    Detects target modality from raw user input using weighted lexical pattern matching.
    """
    cleaned = text.lower()

    # Calculate matches per modality
    scores: dict[Modality, int] = {m: 0 for m in Modality}
    for modality, keywords in MODALITY_KEYWORDS.items():
        for kw in keywords:
            # Whole word or boundary match
            if re.search(r"\b" + re.escape(kw) + r"\b", cleaned):
                scores[modality] += 2
            elif kw in cleaned:
                scores[modality] += 1

    best_modality, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        return best_modality
    return default


def detect_audience(text: str, default: AudienceCategory = AudienceCategory.PROFESSIONALS) -> AudienceCategory:
    """
    Detects target audience tier from raw input.
    """
    cleaned = text.lower()
    for audience, keywords in AUDIENCE_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", cleaned):
                return audience
    return default


def resolve_category(modality: Modality, text: str) -> str:
    """
    Resolves the most appropriate category slug based on modality and keywords.
    """
    cleaned = text.lower()

    if modality == Modality.IMAGE:
        if any(w in cleaned for w in ("cinematic", "film", "movie", "dramatic")):
            return "cinematic-image"
        if any(w in cleaned for w in ("photo", "realistic", "real life", "camera")):
            return "photorealistic"
        if any(w in cleaned for w in ("concept", "game", "world", "fantasy")):
            return "concept-art"
        if any(w in cleaned for w in ("3d", "render", "octane", "unreal")):
            return "3d-renders"
        return "cinematic-image"

    elif modality == Modality.VIDEO:
        if any(w in cleaned for w in ("ad", "advertisement", "commercial", "product")):
            return "product-advertisement"
        return "cinematic-video"

    elif modality == Modality.CODE:
        if any(w in cleaned for w in ("python", "fastapi", "async")):
            return "python-engineering"
        if any(w in cleaned for w in ("bug", "fix", "error", "refactor")):
            return "debugging-refactoring"
        if any(w in cleaned for w in ("model", "training", "ml", "neural")):
            return "machine-learning-mlops"
        return "software-development"

    elif modality == Modality.AUDIO:
        return "podcast-voiceover"

    # Default text categories
    if any(w in cleaned for w in ("story", "narrative", "fiction", "novel")):
        return "creative-writing"
    if any(w in cleaned for w in ("summary", "summarize", "tldr", "condense")):
        return "summarization"
    if any(w in cleaned for w in ("strategy", "market", "business", "plan")):
        return "business-strategy"
    if any(w in cleaned for w in ("kid", "child", "school", "learn")):
        return "kids-educational"

    return "general-writing"
