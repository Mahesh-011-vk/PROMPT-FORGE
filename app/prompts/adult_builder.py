"""
PromptForge AI - Adult & Enterprise Professional Prompt Engine.

Constructs rigorous prompts for business strategy, software engineering, financial analysis,
and executive communication with enterprise-grade constraints.
"""

from app.schemas.intent import PromptIntent
from app.schemas.prompt import PromptVariant


class AdultPromptBuilder:
    """Specialized prompt constructor for business, engineering, and executive analysis."""

    def generate_variants(self, intent: PromptIntent, auto_filled: dict[str, str]) -> dict[str, PromptVariant]:
        """Generates structured, professional enterprise prompt variants."""
        subject = intent.subject
        framework = auto_filled.get("framework", "strategic executive briefing")

        # 1. Basic (Concise Executive Request)
        basic_text = (
            f"Provide an actionable, executive-level analysis of {subject}. "
            f"Focus on core strategic trade-offs, financial/operational implications, and prioritized recommendations."
        )
        basic_variant = PromptVariant(
            variant_type="basic",
            title="Executive Action Brief",
            prompt_text=basic_text,
            recommended_settings={"temperature": 0.3, "max_tokens": 800},
        )

        # 2. Advanced (Rigorous Business Framework)
        adv_text = (
            f"You are a Senior Strategic Consultant and Principal Subject-Matter Expert. "
            f"Deliver an exhaustive strategic memorandum addressing: {subject}.\n\n"
            f"Required Analysis Modules:\n"
            f"1. EXECUTIVE SUMMARY: High-level thesis and bottom-line impact in 3 bullets.\n"
            f"2. PROBLEM & ROOT CAUSE DECONSTRUCTION: Systemic bottlenecks and critical dependencies.\n"
            f"3. EVALUATION MATRIX: Compare top 3 alternative approaches using criteria: Cost, Velocity, Risk, and Scalability.\n"
            f"4. IMPLEMENTATION ROADMAP: Phased 30-60-90 day tactical execution plan with explicit KPIs.\n"
            f"5. RISK MITIGATION & GOVERNANCE: Potential failure modes and preventive guardrails.\n\n"
            f"Constraints: Eliminate corporate buzzwords. Support every recommendation with quantitative rationale."
        )
        adv_variant = PromptVariant(
            variant_type="advanced",
            title="Strategic Advisory Memorandum",
            prompt_text=adv_text,
            variables={"subject": subject, "framework": framework},
            recommended_settings={"temperature": 0.2, "max_tokens": 1800},
        )

        # 3. Expert (Deep Technical Architecture & Governance)
        expert_text = (
            f"Act as a Principal Systems Architect and Enterprise Fellow. Conduct a production-grade specification for: {subject}.\n\n"
            f"Deliverable Specifications:\n"
            f"- Architecture & Data Flow: System boundary definitions, state lifecycles, and sequence diagrams.\n"
            f"- Performance & SLA Targets: p95/p99 latency ceilings, concurrency bottlenecks, and resource sizing.\n"
            f"- Security & Zero-Trust Posture: RBAC, secrets management, input sanitization, and compliance (SOC2/GDPR).\n"
            f"- Observability & Telemetry: Distributed tracing, core metric dashboards, and alert thresholds.\n"
            f"- Production Code / Config Artifacts: Complete, production-ready implementation snippets with strict typing.\n\n"
            f"Strict Rule: Do not produce placeholder code ('# TODO'). All code must be complete, tested, and executable."
        )
        expert_variant = PromptVariant(
            variant_type="expert",
            title="Principal Architecture Specification",
            prompt_text=expert_text,
            recommended_settings={"temperature": 0.1, "max_tokens": 2500},
        )

        # 4. Model-Specific (XML-tagged Claude/GPT Reasoning format)
        model_text = (
            f"<role>\n"
            f"You are a world-class strategic operator and enterprise AI specialist.\n"
            f"</role>\n"
            f"<context>\n"
            f"Task: In-depth analysis of {subject}.\n"
            f"</context>\n"
            f"<instructions>\n"
            f"Think step-by-step through first-principles trade-offs before rendering final recommendations.\n"
            f"Output in clear Markdown tables and numbered action items.\n"
            f"</instructions>\n"
            f"<objective>\n"
            f"Provide a definitive playbook on {subject}.\n"
            f"</objective>"
        )
        model_specific_variant = PromptVariant(
            variant_type="model_specific",
            title="XML-Scoped Enterprise Prompt (Claude/GPT-4o)",
            prompt_text=model_text,
            recommended_settings={"format": "xml_tagged"},
        )

        # 5. Structured JSON Spec
        json_spec = {
            "mode": "enterprise_professional",
            "subject": subject,
            "target_audience": "C-Suite & Technical Leadership",
            "analytical_framework": "SWOT + Trade-off Matrix + 30/60/90 Roadmap",
            "constraints": ["Zero placeholders", "Quantitative justification", "Risk mitigation matrix"],
        }
        json_variant = PromptVariant(
            variant_type="structured_json",
            title="Enterprise Analysis JSON Spec",
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


adult_prompt_builder = AdultPromptBuilder()
