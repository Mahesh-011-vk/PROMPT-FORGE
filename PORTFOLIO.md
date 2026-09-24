# PromptForge AI - Portfolio Case Study

> **Tagline:** *"Generate. Optimize. Test. Evaluate. Deploy."*  
> **Target Roles:** Senior AI/ML Engineer | Generative AI Engineer | Principal Backend Systems Architect | LLM Platform Engineer

---

## 1. Executive Summary

**PromptForge AI** is an enterprise-grade AI Prompt Engineering and Lifecycle Management Platform engineered to generate, optimize, benchmark, govern, and deploy production prompts across all generative AI modalities (Text, Image, Video, Code, Audio, Multi-modal).

Unlike generic ChatGPT wrappers or basic CRUD prompt libraries, PromptForge AI solves the real-world operational challenges of enterprise GenAI:
1. **Model Non-Determinism & Ambiguity:** Resolves vague human intent into modular, parameter-rich prompt specifications.
2. **Evaluation & Quality Assurance:** Replaces subjective "vibe checks" with transparent 7-dimensional heuristic scoring and calibrated LLM-as-a-judge pipelines.
3. **Adversarial Safety & Governance:** Defends production models against prompt injection, jailbreaks, and PII leakage using cryptographic nonced sandwiching.
4. **Prompt Version Drift & Auditability:** Treats prompts as mission-critical software artifacts with Git-like immutable commits, line-by-line semantic diffs, and instant rollback.
5. **Observability & Unit Economics:** Employs high-performance Pandas telemetry to track latency percentiles ($p_{50}, p_{90}, p_{95}, p_{99}$) and forecast token burn.

---

## 2. Key Architectural Innovations & Technical Highlights

```
+---------------------------------------------------------------------------------------------------+
|                                      PROMPTFORGE AI ARCHITECTURE                                  |
|                                                                                                   |
|  [ Ingress Gateway ]       [ Security & Auth ]        [ Multi-Agent Graph ]     [ Model Routing ] |
|  - FastAPI Async          - InjectionGuard Scanner   - PlannerAgent             - Circuit Breaker |
|  - Correlation Tracing    - Nonce Delimiter Sandwich - IntentAgent              - Gemini 1.5 Pro  |
|  - Token Bucket RPM       - PII Redaction Engine     - KnowledgeAgent (RAG)     - OpenAI GPT-4o   |
|                           - JWT Bearer & RBAC        - BuilderAgent             - Claude 3.5      |
|                                                      - CriticAgent              - Ollama Local    |
|                                                      - SafetyAgent              - Mock Fallback   |
|                                                                                                   |
|  [ RAG Vector Engine ]    [ Evaluation Lab ]         [ Version Control ]        [ Analytics ]     |
|  - Recursive Chunker      - 7-Dim Heuristic Rubric   - Immutable Commits        - Pandas Engine   |
|  - Cosine Distance Search - G-Eval LLM Judge         - Line/Word Diff Computer  - p50-p99 Latency |
|  - Semantic Deduplication - Elo A/B Head-to-Head     - Append-Only Rollbacks    - Cost Forecast   |
+---------------------------------------------------------------------------------------------------+
```

### 1. Autonomous Multi-Agent Prompt Synthesis
- **Blackboard Architecture:** A shared `AgentState` object passes sequentially through 6 autonomous nodes (`PlannerAgent` $\rightarrow$ `IntentAgent` $\rightarrow$ `KnowledgeAgent` $\rightarrow$ `BuilderAgent` $\rightarrow$ `CriticAgent` $\rightarrow$ `SafetyAgent`).
- **Complete Trace Auditability:** Every agent step logs its thought process, output summary, token count, and millisecond latency.

### 2. Specialized Modality Compilers
- **Image Prompts:** Injects volumetric lighting, ARRI Alexa optical framing, 35mm/85mm focal depths, Unreal Engine 5 surface textures, and negative constraints.
- **Video Prompts:** Formats camera trajectory directives (dolly-in, crane pan, drone reveal), temporal frame rates (24fps/60fps motion blur), and artifact constraints.
- **Code Prompts:** Enforces explicit typing, Big-O complexity documentation, boundary validation, and zero-placeholder directives.
- **Audience Guardrails:** Features dedicated Kids Mode (curated vocabulary, playful analogies) and Adult/Enterprise Mode.

### 3. RAG Knowledge Base & Semantic Deduplication
- **Recursive Markdown Chunker:** Context-aware sliding window chunker preserving headings and syntax blocks.
- **Dense Vector Search:** 768-dimensional vector space evaluated using high-speed cosine similarity.
- **Hybrid Deduplication:** SHA-256 cryptographic exact match check combined with semantic vector distance gating ($0.88$ similarity threshold) to prevent prompt redundancy.

### 4. 7-Dimensional Heuristic Quality Lab & LLM-as-a-Judge
- **Deterministic Rubric:** Scores prompts across Clarity (1.2x), Specificity (1.3x), Context & Persona (1.0x), Constraints (1.2x), Output Format (1.1x), Safety (1.5x), and Ambiguity Control (1.0x).
- **G-Eval LLM Judge:** Structured evaluator providing actionable chain-of-thought feedback for model alignment.
- **Elo A/B Comparison:** Blind comparative testing declaring statistically grounded prompt winners.

### 5. Git-Like Immutable Version Control
- **Semantic Version Commits:** Every prompt update advances an immutable version counter (`v1`, `v2`, `v3`) with mandatory change logs.
- **Line & Word-Level Diffing:** Powered by `difflib.SequenceMatcher`, calculating addition/deletion counts and similarity ratios.
- **Append-Only Rollbacks:** Reverting to a historical version commits a new forward version, preserving audit trail integrity.

### 6. Defense-in-Depth Security
- **InjectionGuard:** Pattern scanner detecting direct instruction resets, persona hijacking (DAN), developer mode simulations, and system prompt leaks.
- **Sandwich Defense:** Wraps untrusted input inside cryptographically random 16-hex nonced XML delimiters (`<user_data_{nonce}>`).
- **PII Scrubber:** Automated redaction of emails, credit cards, SSNs, phone numbers, and API keys.
- **Rate Limiting:** In-memory token bucket sliding window preventing brute force and DDoS abuse.

### 7. Data Engineering Telemetry (Pandas & NumPy)
- Emits granular `UsageEvent` records tracking model, tokens, latency, cost, and status.
- Computes empirical percentiles ($p_{50}, p_{90}, p_{95}, p_{99}$) and projects 7-day and 30-day budget burn velocity.

### 8. Python-First Glassmorphic UI (NiceGUI + Plotly)
- Sleek dark glassmorphic dashboard with live Plotly charts.
- Dedicated interactive workspaces: Prompt Studio, Prompt Optimizer, Evaluation Lab, Prompt Library, and System Settings.

---

## 3. Technology Stack & Design Decisions

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (ASGI) | Async-native, high throughput, automated OpenAPI documentation |
| **Language & Typing** | Python 3.12+ / 3.13 | Modern type annotations, dataclasses, pattern matching |
| **Frontend UI** | NiceGUI + Plotly | Pure Python full-stack reactive interface; zero JavaScript build fatigue |
| **Database ORM** | SQLAlchemy 2.0 Async | Async session lifecycle, PostgreSQL + pgvector ready, SQLite dev fallback |
| **Data Engineering** | Pandas + NumPy | Fast vector operations, percentile distributions, cost forecasting |
| **Security & Auth** | bcrypt + python-jose | Salted 12-round password hashing, stateless JWT bearer authorization |
| **Model Router** | Custom Resilient Router | Multi-provider abstraction (Gemini, OpenAI, Anthropic, Ollama, Mock) + Circuit Breaker |
| **Packaging & CI** | Hatchling, Docker, Compose | Multi-stage builder runtime, non-root user security |

---

## 4. Verification & Quality Metrics

- **Test Suite:** **65 / 65 tests passing** (`pytest`) across unit, integration, and end-to-end workflows.
- **Lint & Style:** **Zero Ruff warnings**; conforms to strict PEP 8, Flake8, and Bandit security standards.
- **Execution Speed:** Full test suite executes in **~3.5 seconds**.
- **Container Readiness:** Multi-stage `Dockerfile` with non-root security user (`uid 10001`) and automated healthcheck probes.

---

## 5. Resume Bullet Points (Copy & Paste)

### For Senior AI/ML Engineer / Generative AI Engineer:
- *Architected **PromptForge AI**, an enterprise GenAI Prompt Engineering and Evaluation platform featuring autonomous 6-agent synthesis (Planner, Intent, Knowledge, Builder, Critic, Safety), RAG vector retrieval, and 7-dimensional heuristic quality scoring.*
- *Implemented multi-modal compilation engines for text, photorealistic image, cinematic video, and code prompting, achieving automated parameterization and negative constraint injection.*
- *Constructed defense-in-depth LLM security pipelines including `InjectionGuard` adversarial payload detection, automated PII scrubbing, and cryptographic nonced sandwich wrapping to neutralize indirect prompt injection attacks.*
- *Engineered a RAG knowledge retrieval and semantic deduplication engine using recursive markdown chunking and 768-dimensional cosine vector similarity.*

### For Principal Backend / Platform Software Architect:
- *Designed an asynchronous enterprise backend in Python 3.12, FastAPI, and SQLAlchemy 2.0 Async, implementing a Git-like immutable prompt version control system with line-by-line semantic diffing and append-only rollbacks.*
- *Built a high-performance telemetry and analytics pipeline using Pandas and NumPy, aggregating request volume, latency percentiles ($p_{50}, p_{95}, p_{99}$), and predictive 30-day budget burn velocity.*
- *Engineered a multi-provider Model Router with circuit-breaker failover across Google Gemini, OpenAI GPT-4o, Anthropic Claude, and local Ollama instances.*
- *Developed a modern reactive dark glassmorphic full-stack UI using NiceGUI and Plotly, delivering real-time prompt generation, A/B evaluation, and telemetry dashboards.*
