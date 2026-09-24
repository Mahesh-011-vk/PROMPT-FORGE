"""
PromptForge AI - Intent Extraction Engine.

Analyzes raw natural language user requests and constructs a structured PromptIntent schema.
"""

import re
from typing import ClassVar

from app.config.constants import AudienceCategory, Modality, SafetyClassification
from app.prompts.taxonomy import detect_audience, detect_modality, resolve_category
from app.schemas.intent import PromptIntent


class IntentExtractor:
    """Extracts structured semantic parameters and constraints from user prompt inputs."""

    # Disallowed / dangerous keyword triggers
    HARMFUL_PATTERNS: ClassVar[list[str]] = [
        r"\b(bomb|explosive|weapon of mass destruction)\b",
        r"\b(malware|ransomware|keylogger|ddos attack tool)\b",
        r"\b(suicide|self-harm instructions)\b",
        r"\b(child sexual|csam|underage explicit)\b",
        r"\b(credit card fraud|steal identity)\b",
    ]

    def extract(
        self,
        raw_input: str,
        modality_override: Modality | None = None,
        category_override: str | None = None,
        audience_override: AudienceCategory | None = None,
        target_model_override: str | None = None,
    ) -> PromptIntent:
        """
        Parses raw text input and produces a validated PromptIntent.
        """
        cleaned = raw_input.strip()

        # 1. Safety classification
        safety = SafetyClassification.SAFE
        for pattern in self.HARMFUL_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                safety = SafetyClassification.DISALLOWED
                break

        # 2. Modality & Category
        modality = modality_override or detect_modality(cleaned)
        category = category_override or resolve_category(modality, cleaned)
        audience = audience_override or detect_audience(cleaned)

        # 3. Subject extraction
        subject = self._extract_subject(cleaned, modality)

        # 4. Environment & Setting
        environment = self._extract_environment(cleaned)

        # 5. Style extraction
        style = self._extract_style(cleaned, modality)

        # 6. Tone
        tone = self._extract_tone(cleaned, audience)

        # 7. Output format
        output_format = self._determine_output_format(cleaned, modality)

        # 8. Constraints
        constraints = self._extract_constraints(cleaned)

        return PromptIntent(
            objective=f"Generate high-fidelity {modality.value} prompt for: {subject}",
            modality=modality,
            category=category,
            audience=audience,
            subject=subject,
            environment=environment,
            style=style,
            tone=tone,
            constraints=constraints,
            output_format=output_format,
            target_model=target_model_override or "default",
            language="English",
            complexity="expert" if audience in (AudienceCategory.EXPERTS, AudienceCategory.DEVELOPERS) else "intermediate",
            safety_classification=safety,
            technical_parameters={},
        )

    def _extract_subject(self, text: str, modality: Modality) -> str:
        """Extracts the primary focal subject from user text."""
        # Strip common prefixes: "Create a...", "Make a...", "Generate a prompt for..."
        cleaned = re.sub(
            r"^(create|make|generate|build|write|draw|show)\s+(an?|the)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()

        # Remove modality words like "cinematic image of", "video of"
        cleaned = re.sub(
            r"^(cinematic\s+)?(image|photo|video|clip|story|code|script)\s+(of|about|showing|for)\s+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()

        # Fallback to trimmed text if extraction was too aggressive
        return cleaned if len(cleaned) > 2 else text

    def _extract_environment(self, text: str) -> str | None:
        """Extracts environment/setting indicators if present."""
        patterns = [
            r"\b(in|at|under|on|inside|across|through)\s+((an?|the)\s+[\w\s]{3,35})(?=[,.]|$)",
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return None

    def _extract_style(self, text: str, modality: Modality) -> str:
        """Detects aesthetic style descriptors."""
        lower = text.lower()
        if "cinematic" in lower:
            return "cinematic film still, volumetric lighting, photorealistic"
        if "anime" in lower or "manga" in lower:
            return "vibrant modern anime style, Makoto Shinkai aesthetic"
        if "3d" in lower or "render" in lower:
            return "octane 3D render, ray tracing, Unreal Engine 5"
        if "minimal" in lower or "clean" in lower:
            return "minimalist, clean lines, elegant typography"

        if modality == Modality.IMAGE:
            return "photorealistic, 8k resolution, professional color grade"
        if modality == Modality.VIDEO:
            return "35mm motion picture aesthetic, smooth frame rate"
        return "structured, authoritative, clear"

    def _extract_tone(self, text: str, audience: AudienceCategory) -> str:
        """Determines appropriate communicative tone."""
        if audience == AudienceCategory.KIDS:
            return "playful, warm, simple, educational, and encouraging"
        if audience == AudienceCategory.DEVELOPERS:
            return "concise, technically rigorous, production-grade, and direct"
        if audience == AudienceCategory.PROFESSIONALS:
            return "executive, strategic, professional, and outcome-oriented"
        return "balanced, clear, informative, and engaging"

    def _determine_output_format(self, text: str, modality: Modality) -> str:
        """Determines the requested or best output format."""
        lower = text.lower()
        if "json" in lower:
            return "JSON"
        if "bullet" in lower or "list" in lower:
            return "markdown list"
        if modality == Modality.CODE:
            return "executable Python script with type annotations"
        if modality in (Modality.IMAGE, Modality.VIDEO):
            return "structured visual prompt specification"
        return "structured markdown"

    def _extract_constraints(self, text: str) -> list[str]:
        """Extracts negative instructions or explicit constraints."""
        constraints: list[str] = []
        lower = text.lower()
        neg_matches = re.findall(r"(?:do not|without|no|exclude|never)\s+([\w\s]{3,30})(?=[,.]|$)", lower)
        for m in neg_matches:
            constraints.append(m.strip())

        # Baseline universal constraints
        if not constraints:
            constraints.append("no hallucinated claims")
            constraints.append("no unnecessary filler or conversational preamble")
        return constraints


intent_extractor = IntentExtractor()
