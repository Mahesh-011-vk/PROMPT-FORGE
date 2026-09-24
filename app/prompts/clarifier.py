"""
PromptForge AI - Smart Clarification Engine.

Detects missing high-value slots without overwhelming the user, offering 1-3 targeted questions
along with intelligent AI auto-fill defaults.
"""

from app.config.constants import Modality
from app.schemas.intent import ClarificationQuestion, ClarificationResult, PromptIntent


class SmartClarifier:
    """Discovers high-leverage missing details and produces quick-answer options."""

    def clarify(self, intent: PromptIntent, user_answers: dict[str, str] | None = None) -> ClarificationResult:
        """
        Evaluates the extracted intent against modality requirements and generates
        clarification questions for missing essential slots.
        """
        answers = user_answers or {}
        questions: list[ClarificationQuestion] = []
        auto_filled: dict[str, str] = {}

        if intent.modality == Modality.IMAGE:
            # 1. Camera / Composition
            if "camera" not in answers:
                questions.append(
                    ClarificationQuestion(
                        slot_name="camera",
                        question="What camera perspective and lens would you prefer?",
                        suggested_options=["Wide-angle 24mm", "Cinematic 35mm anamorphic", "Macro close-up", "Drone aerial"],
                        inferred_default="Wide-angle 35mm anamorphic lens with subtle depth of field",
                        importance="high",
                    )
                )
                auto_filled["camera"] = questions[-1].inferred_default
            else:
                auto_filled["camera"] = answers["camera"]

            # 2. Lighting & Atmosphere
            if "lighting" not in answers:
                questions.append(
                    ClarificationQuestion(
                        slot_name="lighting",
                        question="What lighting and atmospheric mood fits best?",
                        suggested_options=["Golden hour sunlight", "Moody neon cyberpunk", "Soft diffuse studio", "Dramatic volumetric rays"],
                        inferred_default="Dramatic volumetric lighting with subtle rim light and cinematic haze",
                        importance="high",
                    )
                )
                auto_filled["lighting"] = questions[-1].inferred_default
            else:
                auto_filled["lighting"] = answers["lighting"]

        elif intent.modality == Modality.VIDEO:
            # 1. Camera Motion
            if "camera_motion" not in answers:
                questions.append(
                    ClarificationQuestion(
                        slot_name="camera_motion",
                        question="What camera motion should accompany the action?",
                        suggested_options=["Slow tracking push-in", "Dynamic drone orbit", "Handheld documentarian", "Static steadycam"],
                        inferred_default="Smooth forward tracking push-in following focal action",
                        importance="high",
                    )
                )
                auto_filled["camera_motion"] = questions[-1].inferred_default
            else:
                auto_filled["camera_motion"] = answers["camera_motion"]

            # 2. Duration & Pacing
            if "duration" not in answers:
                questions.append(
                    ClarificationQuestion(
                        slot_name="duration",
                        question="What clip duration and pacing are you targeting?",
                        suggested_options=["5-second dynamic reveal", "10-second continuous take", "Slow-motion 60fps study"],
                        inferred_default="5-second continuous cinematic shot with fluid motion physics",
                        importance="medium",
                    )
                )
                auto_filled["duration"] = questions[-1].inferred_default
            else:
                auto_filled["duration"] = answers["duration"]

        elif intent.modality == Modality.CODE:
            # Architecture / Framework
            if "framework" not in answers:
                questions.append(
                    ClarificationQuestion(
                        slot_name="framework",
                        question="Which Python library or architecture framework should be used?",
                        suggested_options=["FastAPI + Pydantic v2", "Pure Python asyncio", "SQLAlchemy 2.0 Async", "CLI with Typer"],
                        inferred_default="FastAPI with Pydantic v2 schemas and strict type annotations",
                        importance="high",
                    )
                )
                auto_filled["framework"] = questions[-1].inferred_default
            else:
                auto_filled["framework"] = answers["framework"]

        else:
            # General Text: depth and format
            if "format" not in answers:
                questions.append(
                    ClarificationQuestion(
                        slot_name="format",
                        question="What structural format would be most actionable?",
                        suggested_options=["Executive Briefing", "Step-by-step Framework", "Bullet Breakdown", "Complete Narrative"],
                        inferred_default="Structured executive briefing with key bullet takeaways",
                        importance="medium",
                    )
                )
                auto_filled["format"] = questions[-1].inferred_default
            else:
                auto_filled["format"] = answers["format"]

        return ClarificationResult(
            has_missing_slots=len(questions) > 0,
            questions=questions,
            auto_filled_values=auto_filled,
        )


smart_clarifier = SmartClarifier()
