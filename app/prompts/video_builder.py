"""
PromptForge AI - Dedicated Video Prompt Engine.

Constructs scene-by-scene video generation prompts tailored for Runway Gen-3, OpenAI Sora,
Kling AI, and Luma Dream Machine.
"""

from app.schemas.intent import PromptIntent
from app.schemas.prompt import PromptVariant, VideoPromptSpec


class VideoPromptBuilder:
    """Specialized prompt constructor for temporal video generation models."""

    def build_spec(self, intent: PromptIntent, auto_filled: dict[str, str]) -> VideoPromptSpec:
        """Converts user intent and clarification slots into a VideoPromptSpec."""
        subject = intent.subject
        camera_motion = auto_filled.get("camera_motion", "Smooth tracking push-in following focal action")
        duration = auto_filled.get("duration", "5 seconds")
        environment = intent.environment or "within a dynamic, atmospheric cinematic setting"

        return VideoPromptSpec(
            scene=f"Opening sequence featuring {subject} {environment}.",
            character=subject,
            action=f"{subject} moving with realistic weight and continuous temporal momentum.",
            environment=environment,
            camera_movement=camera_motion,
            camera_angle="Eye-level cinematic framing shifting to a subtle dynamic low angle",
            lens="35mm anamorphic prime lens, high optical fidelity",
            lighting="Volumetric atmosphere, directional key light with natural environmental reflections",
            motion_speed="Naturalistic real-time motion physics at 24fps film cadence",
            visual_style="Kodak 5219 35mm film stock aesthetic, fine grain, rich color grade",
            audio_description="Subtle ambient room tone, Foley footfalls, and cinematic low-frequency swell",
            dialogue="",
            timing=duration,
            transitions="Continuous unbroken take with seamless temporal continuity",
            negative_constraints="jitter, morphing, jerky motion, flickering, blurry limbs, sudden jumps, deformed geometry",
        )

    def generate_variants(self, spec: VideoPromptSpec, target_model: str = "default") -> dict[str, PromptVariant]:
        """Produces Basic, Advanced, Expert, Model-Specific, and Structured JSON video variants."""

        # 1. Basic
        basic_text = f"Cinematic video clip of {spec.action}, {spec.environment}. Camera: {spec.camera_movement}."
        basic_variant = PromptVariant(
            variant_type="basic",
            title="Concise Video Prompt",
            prompt_text=basic_text,
            negative_prompt=spec.negative_constraints,
            recommended_settings={"duration_sec": 5, "motion_bucket": 127},
        )

        # 2. Advanced
        adv_text = (
            f"A continuous cinematic shot: {spec.scene} "
            f"Action: {spec.action}. "
            f"Camera movement: {spec.camera_movement} using {spec.lens}. "
            f"Lighting & Mood: {spec.lighting}. "
            f"Visual cadence: {spec.visual_style}, {spec.motion_speed}."
        )
        adv_variant = PromptVariant(
            variant_type="advanced",
            title="Production Video Prompt",
            prompt_text=adv_text,
            negative_prompt=spec.negative_constraints,
            variables={"subject": spec.character, "camera": spec.camera_movement, "action": spec.action},
            recommended_settings={"fps": 24, "duration": spec.timing, "guidance_scale": 7.0},
        )

        # 3. Expert Structured Breakdown (Industry Tagged Format)
        expert_text = (
            f"[SCENE]: {spec.scene}\n"
            f"[CHARACTER / SUBJECT]: {spec.character}\n"
            f"[ACTION]: {spec.action}\n"
            f"[ENVIRONMENT]: {spec.environment}\n"
            f"[CAMERA MOVEMENT]: {spec.camera_movement} ({spec.camera_angle}, {spec.lens})\n"
            f"[LIGHTING]: {spec.lighting}\n"
            f"[MOTION & PHYSICS]: {spec.motion_speed}\n"
            f"[VISUAL STYLE]: {spec.visual_style}\n"
            f"[AUDIO & SOUND DESIGN]: {spec.audio_description}\n"
            f"[TIMING & CADENCE]: {spec.timing} unbroken take\n"
            f"[NEGATIVE CONSTRAINTS]: {spec.negative_constraints}"
        )
        expert_variant = PromptVariant(
            variant_type="expert",
            title="Director Master Breakdown",
            prompt_text=expert_text,
            negative_prompt=spec.negative_constraints,
            variables={"timing": spec.timing},
            recommended_settings={"camera_control": "enabled", "motion_brush": "foreground"},
        )

        # 4. Model-Specific formatting
        model_lower = target_model.lower()
        if "sora" in model_lower:
            model_text = (
                f"A cinematic high-resolution video showing {spec.action}. "
                f"The camera executes a {spec.camera_movement.lower()}. "
                f"Setting: {spec.environment}. Lighting: {spec.lighting}. "
                f"Filmic texture with natural motion blur, realistic temporal consistency, photorealistic textures."
            )
            model_title = "OpenAI Sora Optimized"
        elif "runway" in model_lower or model_lower == "default":
            model_text = (
                f"{spec.character} {spec.action}, {spec.environment}. "
                f"Camera: {spec.camera_movement}. Cinematic lighting, 35mm film still in motion. "
                f"--motion 5 --interpolate"
            )
            model_title = "Runway Gen-3 Alpha Formatted"
        else:
            model_text = f"{adv_text} --fps 24 --duration {spec.timing}"
            model_title = f"{target_model.capitalize()} Formatted"

        model_specific_variant = PromptVariant(
            variant_type="model_specific",
            title=model_title,
            prompt_text=model_text,
            negative_prompt=spec.negative_constraints,
            recommended_settings={"target_model": target_model},
        )

        # 5. Structured JSON
        json_variant = PromptVariant(
            variant_type="structured_json",
            title="Video Prompt JSON Specification",
            prompt_text=spec.model_dump_json(indent=2),
            structured_json=spec.model_dump(),
            recommended_settings={"format": "JSON"},
        )

        return {
            "basic": basic_variant,
            "advanced": adv_variant,
            "expert": expert_variant,
            "model_specific": model_specific_variant,
            "structured_json": json_variant,
        }


video_prompt_builder = VideoPromptBuilder()
