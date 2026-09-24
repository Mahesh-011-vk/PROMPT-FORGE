"""
PromptForge AI - Dedicated Image Prompt Engine.

Builds structured visual prompts optimized for Midjourney v6, Stable Diffusion XL, FLUX.1,
and model-neutral photorealistic engines.
"""

from app.schemas.intent import PromptIntent
from app.schemas.prompt import ImagePromptSpec, PromptVariant


class ImagePromptBuilder:
    """Specialized prompt constructor for image synthesis models."""

    def build_spec(self, intent: PromptIntent, auto_filled: dict[str, str]) -> ImagePromptSpec:
        """Converts intent and slot filling into a structured ImagePromptSpec."""
        subject = intent.subject
        environment = intent.environment or auto_filled.get("environment", "in a detailed, atmospheric environment")
        camera = auto_filled.get("camera", "shot on ARRI Alexa 65, 35mm anamorphic lens")
        lighting = auto_filled.get("lighting", "cinematic volumetric lighting with subtle rim light")
        style = intent.style or "cinematic film still, photorealistic"

        return ImagePromptSpec(
            subject=subject,
            environment=environment,
            composition="wide-angle cinematic framing, rule of thirds, deep focal depth",
            camera=camera,
            lens="35mm anamorphic lens, shallow depth of field, f/2.0 aperture",
            lighting=lighting,
            color_palette="rich cinematic color grading, balanced contrasts, deep shadows",
            style=style,
            materials="natural surface textures, realistic reflections, tangible micro-details",
            textures="crisp detailed textures, authentic skin/material grain, 8k resolution",
            mood="evocative, awe-inspiring, immersive atmosphere",
            time_of_day="dramatic twilight with ambient fill",
            weather="atmospheric mist, clear air clarity",
            depth_of_field="f/2.0 shallow focus, smooth cinematic bokeh in background",
            quality="masterpiece, photorealistic 8k, Unreal Engine 5 render fidelity",
            negative_prompt="blurry, distorted, deformed, extra limbs, bad anatomy, text, watermark, signature, cartoon, oversaturated, low quality, artifacts",
        )

    def generate_variants(self, spec: ImagePromptSpec, target_model: str = "default") -> dict[str, PromptVariant]:
        """Generates Basic, Advanced, Expert, Model-Specific, and Structured JSON variants."""

        # 1. Basic (Concise)
        basic_text = f"A {spec.style} of {spec.subject} {spec.environment}, {spec.lighting}."
        basic_variant = PromptVariant(
            variant_type="basic",
            title="Concise Visual Prompt",
            prompt_text=basic_text,
            negative_prompt=spec.negative_prompt,
            recommended_settings={"aspect_ratio": "16:9", "steps": 30},
        )

        # 2. Advanced (Detailed)
        adv_text = (
            f"A high-fidelity {spec.style} capturing {spec.subject}, {spec.environment}. "
            f"{spec.composition}. {spec.camera}, {spec.lens}. "
            f"Lighting: {spec.lighting}. Color palette: {spec.color_palette}. "
            f"Atmosphere: {spec.mood}, {spec.time_of_day}."
        )
        adv_variant = PromptVariant(
            variant_type="advanced",
            title="Professional Production Prompt",
            prompt_text=adv_text,
            negative_prompt=spec.negative_prompt,
            variables={"subject": spec.subject, "lighting": spec.lighting, "camera": spec.camera},
            recommended_settings={"aspect_ratio": "16:9", "cfg_scale": 7.0, "steps": 40},
        )

        # 3. Expert (Hyper-Specified with materials and rendering tags)
        expert_text = (
            f"Cinematic masterpiece film still of {spec.subject}, situated {spec.environment}. "
            f"Composition: {spec.composition}, {spec.depth_of_field}. "
            f"Captured on {spec.camera}, equipped with {spec.lens}. "
            f"Lighting design: {spec.lighting}, volumetric god rays, subtle lens flare. "
            f"Surface details: {spec.materials}, {spec.textures}. "
            f"Color grading: {spec.color_palette}. Ambient conditions: {spec.time_of_day}, {spec.weather}. "
            f"Overall fidelity: {spec.quality}."
        )
        expert_variant = PromptVariant(
            variant_type="expert",
            title="Expert Masterclass Prompt",
            prompt_text=expert_text,
            negative_prompt=spec.negative_prompt,
            variables={"subject": spec.subject, "environment": spec.environment},
            recommended_settings={"aspect_ratio": "16:9", "cfg_scale": 7.5, "steps": 50, "sampler": "DPM++ 2M Karras"},
        )

        # 4. Model-Specific formatting
        model_lower = target_model.lower()
        if "midjourney" in model_lower or model_lower == "default":
            model_text = f"{adv_text} --ar 16:9 --v 6.1 --stylize 250 --quality 2"
            model_title = "Midjourney v6.1 Formatted"
        elif "flux" in model_lower:
            model_text = (
                f"A natural color cinematic photograph of {spec.subject}. {spec.environment}. "
                f"Natural optical characteristics of {spec.camera}. {spec.lighting}. "
                f"Naturalistic skin and surface textures without digital sharpening. 35mm film aesthetic."
            )
            model_title = "FLUX.1 Natural Language Prompt"
        else:
            # Stable Diffusion XL format
            model_text = (
                f"{spec.subject}, ({spec.environment}:1.1), ({spec.lighting}:1.2), "
                f"shot on {spec.camera}, {spec.style}, 8k UHD, highly detailed"
            )
            model_title = "Stable Diffusion XL Formatted"

        model_specific_variant = PromptVariant(
            variant_type="model_specific",
            title=model_title,
            prompt_text=model_text,
            negative_prompt=spec.negative_prompt,
            recommended_settings={"target_model": target_model},
        )

        # 5. Structured JSON Variant
        json_variant = PromptVariant(
            variant_type="structured_json",
            title="Structured JSON Prompt Spec",
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


image_prompt_builder = ImagePromptBuilder()
