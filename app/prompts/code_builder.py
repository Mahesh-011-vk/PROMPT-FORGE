"""
PromptForge AI - Dedicated Code & Software Engineering Prompt Engine.

Constructs production-grade prompts for full-stack software development, distributed systems,
data engineering, and cloud architecture with strict typing and zero-placeholder guarantees.
"""

from app.schemas.intent import PromptIntent
from app.schemas.prompt import PromptVariant


class CodePromptBuilder:
    """Specialized prompt constructor for software engineering and technical architecture."""

    def generate_variants(self, intent: PromptIntent, auto_filled: dict[str, str]) -> dict[str, PromptVariant]:
        """Generates structured, production-grade technical prompt variants."""
        subject = intent.subject
        lang = auto_filled.get("language", "Python 3.12+ / TypeScript 5.0+")
        framework = auto_filled.get("framework", "FastAPI / Next.js / Clean Architecture")

        # 1. Basic (Direct Task Execution)
        basic_text = (
            f"You are an expert software engineer. Implement a production-ready solution for: {subject}.\n"
            f"Requirements:\n"
            f"- Use modern {lang} idioms with strict type annotations.\n"
            f"- Include thorough error handling, input validation, and clean module separation.\n"
            f"- Provide executable example usage and core unit tests."
        )
        basic_variant = PromptVariant(
            variant_type="basic",
            title="Concise Engineering Prompt",
            prompt_text=basic_text,
            recommended_settings={"temperature": 0.2, "max_tokens": 1200},
        )

        # 2. Advanced (Modular Engineering Directive)
        adv_text = (
            f"Act as a Senior Software Engineer specializing in {framework}.\n\n"
            f"GOAL: Architect and implement a robust, maintainable solution for: {subject}.\n\n"
            f"SPECIFICATIONS & ARCHITECTURE:\n"
            f"1. DOMAIN MODELING: Define type-safe data structures with strict validation schemas.\n"
            f"2. CORE LOGIC & ALGORITHMIC EFFICIENCY: Optimize for O(1) / O(log N) lookup time and bounded memory.\n"
            f"3. ASYNCHRONY & RESILIENCE: Implement non-blocking asynchronous patterns with timeout and retry guardrails.\n"
            f"4. ERROR DISPATCH: Use custom domain exceptions; never swallow errors with naked try/catch blocks.\n"
            f"5. SECURITY & INPUT SANITIZATION: Protect against injection attacks, path traversals, and malformed payloads.\n\n"
            f"CONSTRAINTS: No placeholder code ('# TODO', '// implement later'). Provide fully functional, runnable code."
        )
        adv_variant = PromptVariant(
            variant_type="advanced",
            title="Modular Production Engineering Directive",
            prompt_text=adv_text,
            variables={"subject": subject, "language": lang},
            recommended_settings={"temperature": 0.15, "max_tokens": 2200},
        )

        # 3. Expert (Principal Systems Architect Master Prompt)
        expert_text = (
            f"[ROLE & COGNITIVE DIRECTIVES]\n"
            f"You are a Principal Systems Architect and Distributed Systems Fellow. "
            f"Design and deliver an exhaustive, battle-tested, production-ready system for: \"{subject}\".\n\n"
            f"[ARCHITECTURAL & SYSTEM DESIGN]\n"
            f"- Pattern: Clean Architecture / Domain-Driven Design (separation of API, Service, Repository, and Model layers).\n"
            f"- Concurrency & Scale: Thread-safe, lock-free where possible, non-blocking asynchronous I/O, connection-pooled.\n"
            f"- Resilience & Fault Tolerance: Circuit breaker pattern, exponential backoff with decorrelated jitter, and idempotent endpoints.\n\n"
            f"[CODE IMPLEMENTATION STANDARDS]\n"
            f"- Typing: 100% strict type hints (Pydantic v2 models, TypeScript strict mode, or typed dataclasses).\n"
            f"- Zero Placeholders Rule: Write every single function completely. Do NOT emit ellipsis (...), '# TODO', or truncated snippets.\n"
            f"- Error Hierarchy: Granular domain-specific exceptions mapped to standardized RFC 7807 problem details.\n\n"
            f"[PERFORMANCE & SLA TARGETS]\n"
            f"- Performance & SLA: Sub-50ms latency ceiling (p99); memory footprint bounded under high concurrency.\n\n"
            f"[SECURITY & ZERO-TRUST POSTURE]\n"
            f"- Security: Zero-Trust Posture with zero-trust input validation, parameterized queries, constant-time token comparison, and OWASP Top 10 mitigation.\n"
            f"- Telemetry: Structured JSON logging with trace_id propagation, metric counters, and health check probes.\n\n"
            f"[TESTING & VERIFICATION SUITE]\n"
            f"- Provide comprehensive automated unit tests covering nominal execution, boundary limits, and edge-case error recovery."
        )
        expert_variant = PromptVariant(
            variant_type="expert",
            title="Principal Systems Architect Master Prompt",
            prompt_text=expert_text,
            negative_prompt="placeholders, todo, mock implementations, unhandled exceptions, any types, unvalidated inputs, synchronous blocking calls in async loops, memory leaks",
            variables={"subject": subject},
            recommended_settings={"temperature": 0.1, "max_tokens": 3500},
        )

        # 4. Model-Specific (XML-Tagged Claude 3.5 / GPT-4o Schema)
        model_text = (
            f"<system_instructions>\n"
            f"You are a world-class code synthesis engine and principal software architect.\n"
            f"Target System Requirement: {subject}\n"
            f"Primary Language/Ecosystem: {lang}\n"
            f"</system_instructions>\n\n"
            f"<technical_rules>\n"
            f"1. Type Safety: Zero 'any' types; comprehensive interfaces, type guards, and generics.\n"
            f"2. Completeness: Never leave placeholder comments or unfinished logic.\n"
            f"3. Security: Sanitize all inputs; enforce safe resource cleanup via context managers or defer.\n"
            f"4. Testing: Include high-coverage automated unit tests with mock fixtures.\n"
            f"</technical_rules>\n\n"
            f"<output_format>\n"
            f"Deliver the solution in structured code blocks with architectural rationale before each module.\n"
            f"</output_format>"
        )
        model_specific_variant = PromptVariant(
            variant_type="model_specific",
            title="XML-Tagged LLM Code Synthesis Directive",
            prompt_text=model_text,
            recommended_settings={"format": "xml_tagged", "temperature": 0.1},
        )

        # 5. Structured JSON Spec
        json_spec = {
            "mode": "code_engineering",
            "subject": subject,
            "ecosystem": lang,
            "architecture_pattern": "Domain-Driven Design / Clean Architecture",
            "quality_gates": ["zero_placeholders", "strict_types", "unit_tests", "owasp_hardened"],
        }
        json_variant = PromptVariant(
            variant_type="structured_json",
            title="Machine-Readable Engineering Spec",
            prompt_text=f"```json\n{json_spec}\n```",
            structured_json=json_spec,
        )

        return {
            "basic": basic_variant,
            "advanced": adv_variant,
            "expert": expert_variant,
            "model_specific": model_specific_variant,
            "structured_json": json_variant,
        }


code_prompt_builder = CodePromptBuilder()
