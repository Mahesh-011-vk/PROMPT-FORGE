# PromptForge AI - AI Generation & Multi-Agent Pipeline

> **Module:** `app.prompts` & `app.agents`  
> **Role:** Multi-Modal Compilation & Autonomous Collaborative Prompt Synthesis

---

## 1. Autonomous Multi-Agent Graph Architecture

Prompt synthesis in PromptForge AI operates as a collaborative multi-agent pipeline sharing an inspectable state blackboard (`AgentState`).

```
                    +------------------------------------+
                    |            User Goal               |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |          PlannerAgent              |
                    |  Deconstructs goals & milestones   |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |           IntentAgent              |
                    |  Extracts persona, tone & format   |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |          KnowledgeAgent            |
                    |  RAG Vector Retrieval (Manuals)    |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |          BuilderAgent              |
                    |  Compiles structured modular draft |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |           CriticAgent              |
                    |  Heuristic audit & constraint test |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |           SafetyAgent              |
                    |  Injection check & age alignment   |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |            Finalizer               |
                    |  Assembled Production Artifact     |
                    +------------------------------------+
```

### Agent Roles & Deliverables

| Agent | Responsibility | Key Output |
| :--- | :--- | :--- |
| **PlannerAgent** | Decomposes raw goal into sub-requirements | Execution plan, target complexity, modality confirmation |
| **IntentAgent** | Resolves target persona, tone, and audience | Calibrated persona (e.g. Staff Architect), tone, output format |
| **KnowledgeAgent** | Queries vector RAG store for domain guidelines | Few-shot exemplars, technical tags, best-practice snippets |
| **BuilderAgent** | Constructs parameterized modular draft | Full prompt text, negative prompt, template variables |
| **CriticAgent** | Adversarial review checking clarity and ambiguity | Quality score (0-10), strengths, weaknesses, suggestions |
| **SafetyAgent** | Scans for prompt injection and audience safety | Verdict (`APPROVED`, `WARNING`, `BLOCKED`), risk flags |

---

## 2. Specialized Modality Engines

PromptForge AI implements dedicated builder engines optimized for the unique prompting grammar of different AI modalities:

### 1. Image Builder (`ImagePromptSpec`)
- **Lighting Dynamics:** Volumetric rays, rim lighting, HDR ambient bounce, golden hour.
- **Optics & Framing:** 35mm / 85mm prime lenses, f/1.4 aperture bokeh, rule-of-thirds, Hasselblad medium format.
- **Surface Rendering:** Unreal Engine 5, Octane render, ray tracing, subsurface skin scattering.
- **Negative Prompts:** Automated negative injection (`bad hands, distorted anatomy, text, watermark`).

### 2. Video Builder (`VideoPromptSpec`)
- **Camera Trajectories:** Dolly-in, crane pan, drone reveal, tracking whip pan.
- **Temporal Dynamics:** 24fps motion blur, fluid physics, atmospheric mist transitions.
- **Negative Constraints:** Jittery cuts, flickering, morphing artifacts, stutter.

### 3. Code Engineering Builder
- **Typing & Idiosyncrasies:** Modern language features, explicit typing, Big-O complexity documentation.
- **Resilience:** Boundary input validation, asynchronous error handling, unit test requirements.
- **Zero Placeholders:** Strict anti-laziness directives forbidding `# TODO` or omitted implementations.

### 4. Kids Educational Builder
- **Tone:** Encouraging, enthusiastic, warm, and highly engaging.
- **Pedagogy:** Playful real-world analogies (pizza fractions, animal superpowers), interactive mini-quizzes.
- **Child Safety:** Strict exclusion of violent or frightening themes.

---

## 3. Template Engine & Variable Syntax

The template engine supports parametric prompts with optional defaults and string transformations:

```jinja2
A cinematic portrait of a {{character_role | capitalize}}, in {{location | upper}},
lighting is {{lighting_style | default: golden hour}}, shot on {{camera | default='Arri Alexa'}}.
```

Supported filters:
- `upper`: Converts string to uppercase.
- `lower`: Converts string to lowercase.
- `capitalize`: Capitalizes first letter.
- `title`: Converts to title case.
- `trim`: Strips leading/trailing whitespace.
- `default: <val>`: Provides fallback value when variable is omitted.
