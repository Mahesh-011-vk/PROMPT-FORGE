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
        environment = intent.environment or auto_filled.get("environment", "in a detailed, atmospheric neo-realist environment")
        camera = auto_filled.get("camera", "shot on ARRI Alexa 65 large-format cinema camera")
        lighting = auto_filled.get("lighting", "volumetric ray-traced lighting with dual-tone neon rim light")
        style = intent.style or "cinematic film still, photorealistic masterpiece"

        return ImagePromptSpec(
            subject=subject,
            environment=environment,
            composition="wide-angle cinematic framing, rule of thirds, Dutch angle depth, balanced golden ratio",
            camera=camera,
            lens="35mm anamorphic prime lens, f/1.8 aperture, creamy bokeh, shallow depth of field",
            lighting=lighting,
            color_palette="Kodak Vision3 500T 35mm film grade, teal and amber split-toning, deep rich shadows",
            style=style,
            materials="weathered carbon fiber, tactile brushed titanium, damp asphalt, micro-scratches",
            textures="subsurface scattering, authentic skin pores, moisture droplets on reflective surfaces, 8k textures",
            mood="evocative, awe-inspiring, moody cyberpunk atmosphere",
            time_of_day="dramatic twilight with ambient fill and specular rain reflections",
            weather="atmospheric mist, particulate suspension, clear optical clarity",
            depth_of_field="f/1.8 shallow focus, smooth cinematic optical falloff",
            quality="8k resolution, photorealistic, masterpiece, Octane Render, Unreal Engine 5.4 Lumen global illumination",
            negative_prompt="blurry, low quality, distortion, noise, oversaturated, deformed hands, extra fingers, warped limbs, bad anatomy, text, watermark, signature, plastic skin, CGI cartoonish, overexposed, artifacting, chromatic aberration, duplicated facial features",
        )

    def generate_variants(self, spec: ImagePromptSpec, target_model: str = "default") -> dict[str, PromptVariant]:
        """Generates Basic, Advanced, Expert, Model-Specific, and Structured JSON variants."""

        # 1. Basic (Concise Visual Prompt)
        basic_text = f"A {spec.style} of {spec.subject}, situated {spec.environment}, {spec.lighting}."
        basic_variant = PromptVariant(
            variant_type="basic",
            title="Concise Visual Prompt",
            prompt_text=basic_text,
            negative_prompt=spec.negative_prompt,
            recommended_settings={"aspect_ratio": "16:9", "steps": 30},
        )

        # 2. Advanced (Production-Ready Photographic Prompt)
        adv_text = (
            f"A high-end cinematic photograph of {spec.subject}, {spec.environment}. "
            f"Composition: {spec.composition}, {spec.depth_of_field}. "
            f"Optics: {spec.camera}, {spec.lens}. "
            f"Lighting: {spec.lighting}, chiaroscuro contrast. "
            f"Textures & Materials: {spec.materials}, {spec.textures}. "
            f"Color science: {spec.color_palette}. Atmosphere: {spec.mood}, {spec.time_of_day}."
        )
        adv_variant = PromptVariant(
            variant_type="advanced",
            title="Professional Production Prompt",
            prompt_text=adv_text,
            negative_prompt=spec.negative_prompt,
            variables={"subject": spec.subject, "lighting": spec.lighting, "camera": spec.camera},
            recommended_settings={"aspect_ratio": "16:9", "cfg_scale": 7.0, "steps": 40},
        )

        # 3. Expert (Comprehensive Master Prompt with Layered Structural Directives)
        expert_text = (
            f"[SCENE & SUBJECT]\n"
            f"An evocative cinematic film still capturing {spec.subject}, situated {spec.environment}. "
            f"Grounded physical presence, authentic styling, micro-expressions conveying deep focus and immersion.\n\n"
            f"[CINEMATOGRAPHY & OPTICS]\n"
            f"Composition: {spec.composition}, {spec.depth_of_field}.\n"
            f"Optics: {spec.camera} with {spec.lens}. Shutter speed 1/125s, ISO 200, f/1.8 aperture for creamy background separation and natural optical distortion.\n\n"
            f"[LIGHTING DESIGN & ATMOSPHERE]\n"
            f"Lighting: {spec.lighting}. Dramatic chiaroscuro key lighting, atmospheric volumetric fog catching neon specular highlights, soft ambient bounce fill.\n\n"
            f"[SURFACES, MATERIALS & TEXTURES]\n"
            f"Materials: {spec.materials}. Tactile micro-details, realistic subsurface scattering, {spec.textures}, authentic moisture condensation.\n\n"
            f"[COLOR SCIENCE & POST-PROCESSING]\n"
            f"Color Grading: {spec.color_palette}. Preserved highlight roll-off, rich dynamic range, Aces color space, subtle film grain.\n\n"
            f"[RENDER FIDELITY ENGINE]\n"
            f"{spec.quality}, ray-traced reflections, extreme optical clarity."
        )
        expert_variant = PromptVariant(
            variant_type="expert",
            title="Photographic Masterclass Directive",
            prompt_text=expert_text,
            negative_prompt=spec.negative_prompt,
            variables={"subject": spec.subject, "environment": spec.environment},
            recommended_settings={"aspect_ratio": "16:9", "cfg_scale": 7.5, "steps": 50, "sampler": "DPM++ 2M Karras"},
        )

        # 4. Model-Specific formatting (Midjourney v6.1 / FLUX.1 / SDXL)
        model_lower = target_model.lower()
        if "midjourney" in model_lower or model_lower == "default":
            model_text = (
                f"A high-end cinematic photo of {spec.subject}, {spec.environment}, "
                f"composition: {spec.composition}, {spec.depth_of_field}, "
                f"lighting: {spec.lighting}, chiaroscuro contrast, atmospheric volumetric fog, "
                f"shot on {spec.camera} with {spec.lens}, "
                f"tactile surfaces: {spec.materials}, {spec.textures}, "
                f"color science: {spec.color_palette}, "
                f"photorealistic cinematic render, 8k resolution, octane render, Unreal Engine 5.4 Lumen --ar 16:9 --v 6.1 --stylize 250 --quality 2"
            )
            model_title = "Midjourney v6.1 Formatted"
        elif "flux" in model_lower:
            model_text = (
                f"A natural color cinematic photograph of {spec.subject}. {spec.environment}. "
                f"Natural optical characteristics of {spec.camera} with {spec.lens}. {spec.lighting}. "
                f"Tactile {spec.materials}, natural skin and surface micro-textures without artificial digital sharpening. "
                f"35mm film aesthetic, authentic optical depth of field."
            )
            model_title = "FLUX.1 Natural Language Prompt"
        else:
            model_text = (
                f"masterpiece, photorealistic 8k photo of {spec.subject}, ({spec.environment}:1.1), "
                f"({spec.lighting}:1.2), shot on {spec.camera} with {spec.lens}, "
                f"{spec.materials}, {spec.style}, 8k UHD, highly detailed, octane render"
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
