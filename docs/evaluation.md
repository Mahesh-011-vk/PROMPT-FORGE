# PromptForge AI - Evaluation Lab & Scoring System

> **Module:** `app.evaluators`  
> **Role:** Heuristic Quality Scoring, LLM-as-a-Judge, A/B Testing, and Offline Benchmarking

---

## 1. 7-Dimensional Heuristic Quality Rubric

Every prompt evaluated by PromptForge AI is scored against 7 empirical dimensions (each scored 0–100):

| Dimension | Weight | Target Metric / Evaluation Criteria |
| :--- | :---: | :--- |
| **1. Clarity** | 1.2 | Syntactic readability, concise sentence structures, absence of double negatives. |
| **2. Specificity** | 1.3 | Penalizes subjective filler ("good", "nice", "awesome"); rewards quantitative metrics and concrete nouns. |
| **3. Context & Persona** | 1.0 | Presence of explicit domain role ("Act as Staff Architect", "Senior Concept Artist") and situational background. |
| **4. Constraints & Rules** | 1.2 | Verifies presence of negative boundaries, forbidden phrasing, and edge-case limits. |
| **5. Output Formatting** | 1.1 | Demands structured deliverables (JSON schema, markdown tables, explicit schemas). |
| **6. Safety & Alignment** | 1.5 | Scans for policy violations, dangerous keywords, and malicious jailbreak payloads. |
| **7. Ambiguity Control** | 1.0 | Penalizes open-ended vagueness ("do whatever you want", "make it cool"); measures directive precision. |

### Overall Score Calculation
$$\text{Overall Score} = \frac{\sum_{i=1}^7 (\text{Score}_i \times \text{Weight}_i)}{\sum_{i=1}^7 \text{Weight}_i}$$

---

## 2. LLM-as-a-Judge Evaluation

In addition to deterministic heuristic rules, PromptForge AI provides simulated and production LLM-as-a-judge scoring following G-Eval and MT-Bench methodologies:
- Formats prompt inside an adversarial judge template.
- Directs model to score candidate on a calibrated 1–10 scale.
- Demands itemized chain-of-thought justification for every point deducted.
- Parses structured score and rationale from JSON output.

---

## 3. Elo A/B Comparison Engine

PromptForge AI enables blind head-to-head prompt comparisons:
- Evaluates Prompt A and Prompt B across all 7 dimensions.
- Computes victory margin and delta percentages.
- Declares winner (`PROMPT_A`, `PROMPT_B`, or `TIE`).
- Produces comparative strengths and weaknesses breakdown.

---

## 4. Offline Benchmark Suite

The platform includes offline evaluation datasets in `/datasets`:
- `image_prompts.jsonl`
- `video_prompts.jsonl`
- `coding_prompts.jsonl`
- `marketing_prompts.jsonl`
- `education_prompts.jsonl`

The benchmark runner executes batch evaluations across test suites, reporting mean scores, variance, and regression alerts across prompt iterations.
