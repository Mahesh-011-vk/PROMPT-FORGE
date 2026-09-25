"""
PromptForge AI - Dedicated Child-Safe Educational Prompt Engine.

Ensures age-appropriate vocabulary, educational milestone alignment, gentle positive reinforcement,
and strict exclusion of mature or unsafe instructions.
"""

from typing import ClassVar

from app.schemas.intent import PromptIntent
from app.schemas.prompt import PromptVariant


class KidsPromptBuilder:
    """Specialized prompt constructor for children's learning, stories, and creativity."""

    SAFE_CHILD_RULES: ClassVar[list[str]] = [
        "Use simple, warm, and uplifting vocabulary suitable for elementary age children.",
        "Emphasize kindness, curiosity, problem solving, and friendship.",
        "Strictly zero violence, scary monsters, dangerous physical instructions, or mature themes.",
        "Include gentle interactive questions to encourage reader curiosity.",
    ]

    def generate_variants(self, intent: PromptIntent, auto_filled: dict[str, str]) -> dict[str, PromptVariant]:
        """Generates age-calibrated, safe educational prompt variants."""
        subject = intent.subject
        setting = intent.environment or "a colorful and cheerful world"

        # 1. Basic (Short Story Prompt)
        basic_text = (
            f"Write a cheerful, easy-to-read educational story for kids about {subject} {setting}. "
            f"Use simple words, fun sound effects (like 'swoosh!' or 'beep!'), and teach a positive lesson."
        )
        basic_variant = PromptVariant(
            variant_type="basic",
            title="Fun Children's Story Prompt",
            prompt_text=basic_text,
            recommended_settings={"temperature": 0.7, "max_tokens": 600},
        )

        # 2. Advanced (Interactive Learning Adventure)
        adv_text = (
            f"You are a friendly, imaginative children's educator and storyteller. "
            f"Create an engaging learning adventure about {subject} {setting}.\n\n"
            f"Instructions:\n"
            f"1. Audience: Children aged 6-9 years old.\n"
            f"2. Tone: Warm, encouraging, playful, and curious.\n"
            f"3. Vocabulary: Short sentences, vivid sensory words, easy-to-follow explanations.\n"
            f"4. Educational Goal: Help the child understand how {subject} works through a relatable analogy.\n"
            f"5. Interactive Moment: Pause twice in the story to ask the child a fun question (e.g., 'What do you think happens next?').\n"
            f"6. Safety: Strictly safe, friendly, and non-threatening content only."
        )
        adv_variant = PromptVariant(
            variant_type="advanced",
            title="Interactive Learning Adventure",
            prompt_text=adv_text,
            variables={"subject": subject, "age_tier": "6-9 years old"},
            recommended_settings={"temperature": 0.6, "max_tokens": 1000},
        )

        # 3. Expert (Educational Curriculum & Activity Builder)
        expert_text = (
            f"Design a complete mini-learning module for kids exploring {subject}.\n\n"
            f"Structure your response into 4 kid-friendly sections:\n"
            f"1. THE CURIOUS DISCOVERY: A 300-word story introducing {subject} with gentle humor.\n"
            f"2. DID YOU KNOW? 3 fascinating, easy-to-understand science/world facts.\n"
            f"3. KITCHEN-TABLE ACTIVITY: A 100% safe, fun, hands-on craft or drawing challenge using common household items.\n"
            f"4. STAR BADGE CHALLENGE: 2 gentle riddle questions to review what they learned.\n\n"
            f"Safety Guardrails: Zero sharp objects, zero heat/chemical exposure, zero scary imagery. Positive reinforcement only."
        )
        expert_variant = PromptVariant(
            variant_type="expert",
            title="Complete STEM Curriculum & Craft Prompt",
            prompt_text=expert_text,
            negative_prompt="scary, violence, monsters, complex jargon, dark themes, unsafe physical instructions",
            recommended_settings={"temperature": 0.5, "max_tokens": 1500},
        )

        # 4. Model-Specific (LLM Educational Assistant formatting)
        model_text = (
            f"<system_instruction>\n"
            f"You are Sparky, an enthusiastic AI tutor designed for young learners. "
            f"Never explain anything using jargon. Always validate the child's questions with praise.\n"
            f"</system_instruction>\n"
            f"<user_prompt>\n"
            f"Can you explain {subject} to me in a really fun story?\n"
            f"</user_prompt>"
        )
        model_specific_variant = PromptVariant(
            variant_type="model_specific",
            title="System-Guarded Child AI Companion",
            prompt_text=model_text,
            recommended_settings={"system_prompt": "enabled"},
        )

        # 5. Structured JSON
        json_spec = {
            "mode": "child_safe_educational",
            "subject": subject,
            "target_age": "6-9",
            "core_concept": subject,
            "story_setting": setting,
            "safety_rules": self.SAFE_CHILD_RULES,
        }
        json_variant = PromptVariant(
            variant_type="structured_json",
            title="Kid-Safe JSON Specification",
            prompt_text=str(json_spec),
            structured_json=json_spec,
            recommended_settings={"format": "JSON"},
        )

        return {
            "basic": basic_variant,
            "advanced": adv_variant,
            "expert": expert_variant,
            "model_specific": model_specific_variant,
            "structured_json": json_variant,
        }


kids_prompt_builder = KidsPromptBuilder()
