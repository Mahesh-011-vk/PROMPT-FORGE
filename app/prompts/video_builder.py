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
        camera_motion = auto_filled.get("camera_motion", "Continuous dynamic 360-degree orbital tracking shot smoothly pushing in")
        duration = auto_filled.get("duration", "8 seconds")
        environment = intent.environment or "within a dynamic, atmospheric neo-noir cinematic environment"

        return VideoPromptSpec(
            scene=f"High-resolution cinematic sequence depicting {subject} {environment}.",
            character=subject,
            action=f"{subject} moving with authentic weight, lifelike biomechanics, and unbroken temporal momentum.",
            environment=environment,
            camera_movement=camera_motion,
            camera_angle="Low-angle cinematic hero framing smoothly rotating to eye-level profile",
            lens="35mm anamorphic prime lens, T1.5, authentic optical depth of field",
            lighting="Volumetric atmospheric haze, directional key lighting with dynamic specular environmental reflections",
            motion_speed="Naturalistic real-time motion physics at 24fps film cadence, organic optical motion blur",
            visual_style="Kodak Vision3 5219 35mm film stock aesthetic, organic fine grain, rich color grade, high dynamic range",
            audio_description="Spatial binaural foley, subtle environmental room tone, and low-frequency cinematic undertone swell",
            dialogue="",
            timing=duration,
            transitions="Continuous unbroken sequence with seamless temporal coherence and consistent character identity",
            negative_constraints="jitter, temporal morphing, jerky motion, frame skipping, deformed geometry, unnatural physics, flickering, blurry limbs, sudden jumps, artifacts, camera stutter, bad anatomy",
        )

    def generate_variants(self, spec: VideoPromptSpec, target_model: str = "default") -> dict[str, PromptVariant]:
        """Produces Basic, Advanced, Expert, Model-Specific, and Structured JSON video variants."""

        # 1. Basic (Concise Video Prompt)
        basic_text = f"Cinematic video clip of {spec.action}, situated {spec.environment}. Camera: {spec.camera_movement}."
        basic_variant = PromptVariant(
            variant_type="basic",
            title="Concise Video Prompt",
            prompt_text=basic_text,
            negative_prompt=spec.negative_constraints,
            recommended_settings={"duration_sec": 5, "motion_bucket": 127},
        )

        # 2. Advanced (Production Video Sequence)
        adv_text = (
            f"A continuous cinematic shot: {spec.scene} "
            f"Action: {spec.action}. "
            f"Camera movement: {spec.camera_movement} using {spec.lens}. "
            f"Lighting & Atmosphere: {spec.lighting}. "
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

        # 3. Expert Structured Breakdown (Director Master Sequence)
        expert_text = (
            f"[SCENE]: {spec.scene} Setting: {spec.environment}.\n\n"
            f"[CHARACTER / SUBJECT]: {spec.character}. Action: {spec.action}. "
            f"Realistic physical weight distribution, grounded footwork, unbroken temporal momentum.\n\n"
            f"[CAMERA MOVEMENT]: {spec.camera_movement} ({spec.camera_angle}, {spec.lens}). "
            f"Fluid gimbal stabilization, zero handheld shake, dynamic depth tracking.\n\n"
            f"[LIGHTING & ENVIRONMENTAL DYNAMICS]: {spec.lighting}. Environmental shadows shifting in real-time sync with camera motion, atmospheric particulate suspension catching neon rim light.\n\n"
            f"[MOTION & PHYSICS]: {spec.motion_speed}. Natural optical motion blur, zero frame-to-frame character warping or geometry morphing.\n\n"
            f"[CINEMATOGRAPHY & VISUAL STYLE]: {spec.visual_style}. Preserved skin tones, balanced highlights, Aces color managed.\n\n"
            f"[AUDIO & SOUND DESIGN]: {spec.audio_description}.\n\n"
            f"[TIMING & CADENCE]: {spec.timing} continuous unbroken take. Seamless transition readiness.\n\n"
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

        # 4. Model-Specific formatting (Runway Gen-3 / OpenAI Sora)
        model_lower = target_model.lower()
        if "sora" in model_lower:
            model_text = (
                f"A cinematic 1080p continuous video sequence showing {spec.action}. "
                f"The camera executes a {spec.camera_movement.lower()} with {spec.lens}. "
                f"Environment: {spec.environment}. Lighting: {spec.lighting}. "
                f"Photorealistic textures, temporal consistency, natural motion blur, filmic color grading --motion 6 --duration 10s --fps 24"
            )
            model_title = "OpenAI Sora Optimized"
        elif "runway" in model_lower or model_lower == "default":
            model_text = (
                f"{spec.character} {spec.action}, situated {spec.environment}. "
                f"Camera: {spec.camera_movement}, {spec.camera_angle}. "
                f"Lighting: {spec.lighting}. "
                f"Photorealistic 4k, 60fps fluid motion, atmospheric depth, cinematic film cadence --motion 6 --camera zoom-in-pan"
            )
            model_title = "Runway Gen-3 Alpha Formatted"
        else:
            model_text = f"{adv_text} --fps 24 --duration {spec.timing} --motion 5"
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
