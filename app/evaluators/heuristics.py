"""
PromptForge AI - Multi-Dimensional Heuristic Quality Scorer.

Evaluates prompts across Clarity, Specificity, Context, Constraints, Output Format,
Safety, and Ambiguity. Scores are labeled explicitly as AI-generated heuristic evaluations.
"""

from app.schemas.evaluation import EvaluationMetric


class HeuristicScorer:
    """Heuristic rule-based quality evaluator with transparent breakdown rationale."""

    def evaluate(self, prompt: str, modality: str = "text") -> tuple[float, dict[str, EvaluationMetric], list[str]]:
        """
        Computes 7 core dimensional metrics and returns overall weighted score and feedback.
        """
        text = prompt.strip()
        words = text.split()
        word_count = len(words)
        lower = text.lower()

        metrics: dict[str, EvaluationMetric] = {}
        feedback: list[str] = []

        # 1. Clarity (Sentence structure, absence of confusing double negatives)
        clarity_score = 90.0
        if word_count < 5:
            clarity_score = 45.0
            feedback.append("Prompt is too brief to convey clear objectives.")
        elif word_count > 400:
            clarity_score = 75.0
            feedback.append("Prompt is very dense; consider modularizing with XML or markdown headings.")
        metrics["clarity"] = EvaluationMetric(
            name="Clarity",
            score=clarity_score,
            weight=1.2,
            rationale="Measures syntactic readability and unambiguous statement of task intent.",
        )

        # 2. Specificity (Absence of generic qualifiers like 'good', 'nice')
        spec_score = 85.0
        vague_terms = [w for w in ("good", "cool", "nice", "awesome", "great", "best", "fast", "pretty") if w in lower]
        if vague_terms:
            spec_score = max(40.0, 85.0 - len(vague_terms) * 15.0)
            feedback.append(f"Replace subjective words ({', '.join(vague_terms)}) with concrete technical metrics.")
        if any(char in text for char in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")):
            spec_score = min(100.0, spec_score + 10.0)
        metrics["specificity"] = EvaluationMetric(
            name="Specificity",
            score=spec_score,
            weight=1.3,
            rationale="Evaluates presence of concrete, measurable attributes versus subjective descriptions.",
        )

        # 3. Context & Persona (Setting background, role, or audience)
        context_score = 70.0
        if any(role_token in lower for role_token in ("act as", "you are", "expert", "architect", "consultant", "role", "perspective")):
            context_score += 15.0
        if any(bg_token in lower for bg_token in ("context", "background", "setting", "environment", "domain", "scenario")):
            context_score += 15.0
        metrics["context"] = EvaluationMetric(
            name="Context",
            score=min(100.0, context_score),
            weight=1.0,
            rationale="Determines whether domain context and perspective constraints are framed.",
        )

        # 4. Constraints & Guardrails (Negative constraints or boundaries)
        constraints_score = 65.0
        if any(c in lower for c in ("do not", "without", "no ", "never", "avoid", "exclude", "negative:", "strictly")):
            constraints_score = 92.0
        else:
            feedback.append("Add explicit negative constraints to prevent common hallucinations or unwanted styling.")
        metrics["constraints"] = EvaluationMetric(
            name="Constraints",
            score=constraints_score,
            weight=1.1,
            rationale="Checks whether boundaries, negative filters, and anti-patterns are defined.",
        )

        # 5. Output Format (Requested format: JSON, markdown, code, bullet list)
        format_score = 60.0
        if any(fmt in lower for fmt in ("json", "table", "markdown", "list", "bullet", "code", "steps", "schema", "xml")):
            format_score = 95.0
        else:
            feedback.append("Specify an explicit output structure (e.g. JSON schema, bullet items, markdown table).")
        metrics["output_format"] = EvaluationMetric(
            name="Output Format",
            score=format_score,
            weight=1.0,
            rationale="Verifies if output structural format is declared for deterministic model adherence.",
        )

        # 6. Safety & Legality
        safety_score = 100.0
        if any(bad in lower for bad in ("bomb", "malware", "exploit", "ransomware", "suicide", "fraud")):
            safety_score = 0.0
            feedback.append("SAFETY ALERT: Contains prohibited safety risk tokens.")
        metrics["safety"] = EvaluationMetric(
            name="Safety",
            score=safety_score,
            weight=1.5,
            rationale="Evaluates absence of hazardous, abusive, or violating instructions.",
        )

        # 7. Ambiguity Index (Lower ambiguity -> Higher score)
        ambiguity_penalty = 0.0
        if "?" in text and word_count < 10:
            ambiguity_penalty += 20.0
        if "anything" in lower or "whatever" in lower or "somehow" in lower:
            ambiguity_penalty += 25.0
        ambiguity_score = max(20.0, 95.0 - ambiguity_penalty)
        metrics["ambiguity_control"] = EvaluationMetric(
            name="Ambiguity Control",
            score=ambiguity_score,
            weight=1.0,
            rationale="Measures precision in guiding model reasoning pathways without open-ended vagueness.",
        )

        # Compute weighted overall score
        total_weight = sum(m.weight for m in metrics.values())
        overall_score = sum(m.score * m.weight for m in metrics.values()) / total_weight

        return round(overall_score, 1), metrics, feedback


heuristic_scorer = HeuristicScorer()
