# PromptForge AI - System Architecture

> **Tagline:** Generate. Optimize. Test. Evaluate. Deploy.  
> **Repository:** `PromptForge AI`  
> **Version:** `0.1.0-PROD`

---

## 1. Executive Architecture Overview

PromptForge AI is an enterprise-grade AI Prompt Engineering and Lifecycle Platform engineered to design, evaluate, optimize, secure, and govern production prompts across any generative AI modality (Text, Image, Video, Code, Audio, Multi-modal).

Unlike generic ChatGPT wrappers or simplistic CRUD libraries, PromptForge AI features:
- **Autonomous Multi-Agent Prompt Synthesis** (6 specialized agents: Planner, Intent, Knowledge, Builder, Critic, Safety).
- **Domain-Specific Modality Compilers** (Photorealistic cinematography, camera trajectories, code typing standards, kids safety).
- **Retrieval-Augmented Generation (RAG)** vector search across golden prompt engineering manuals.
- **7-Dimensional Heuristic Quality Scoring & LLM-as-a-Judge Evaluation**.
- **Git-Like Prompt Version Control** with append-only immutable commits and line-by-line semantic diffing.
- **Defense-in-Depth Prompt Security** with injection pattern scanners, nonced XML sandwiching, and automated PII scrubbing.
- **Data Engineering & Analytics Pipeline** powered by Pandas for latency percentile tracking and predictive cost burn modeling.
- **Python-First Glassmorphic Interactive UI** built on NiceGUI and Plotly.

---

## 2. High-Level Component Topology

```
                                      +------------------------------------+
                                      |         Client Applications        |
                                      |  (Browser UI, REST Clients, CLI)   |
                                      +-----------------+------------------+
                                                        |
                                                        v
                                      +-----------------+------------------+
                                      |        API Gateway Layer           |
                                      |   FastAPI + Correlation Tracing    |
                                      |   Token Bucket Rate Limiting (RPM) |
                                      +--------+------------------+--------+
                                               |                  |
                         +---------------------+                  +---------------------+
                         |                                                              |
                         v                                                              v
+------------------------+-------------------+                 +------------------------+-------------------+
|            Security & Governance          |                 |           Authentication & RBAC             |
| - InjectionGuard (Adversarial Scanner)     |                 | - JWT Bearer Token Handler                  |
| - PIIScrubber (Email/SSN/Card/Key Redactor)|                 | - Bcrypt Salting & Verification             |
| - SandwichDefense (Cryptographic Nonces)  |                 | - Role Hierarchy: USER, POWER_USER, ADMIN   |
+------------------------+-------------------+                 +------------------------+-------------------+
                         |                                                              |
                         +---------------------+------------------+---------------------+
                                               |
                                               v
+----------------------------------------------+------------------------------------------------------------+
|                                        Core Application Layer                                             |
|                                                                                                           |
|  +---------------------------+   +----------------------------+   +------------------------------------+  |
|  |   Multi-Agent Graph       |   |   Prompt Generation Engine |   |   Prompt Optimizer & Repair        |  |
|  |   - PlannerAgent          |   |   - Intent Extractor       |   |   - Weakness Diagnostician         |  |
|  |   - IntentAgent           |   |   - Smart Clarifier        |   |   - Modality Rule Injector         |  |
|  |   - KnowledgeAgent (RAG)  |   |   - Specialized Modalities |   |   - Tag-Preserving Translator      |  |
|  |   - BuilderAgent          |   |   - Multi-Variant Compiler |   |   - Before/After Diff Generator    |  |
|  |   - CriticAgent           |   +-------------+--------------+   +------------------------------------+  |
|  |   - SafetyAgent           |                 |                                                          |
|  +-------------+-------------+                 |                                                          |
|                |                               |                                                          |
|                +---------------+---------------+                                                          |
|                                |                                                                          |
|                                v                                                                          |
|  +-----------------------------+------------------------------+   +------------------------------------+  |
|  |              Evaluation & Scoring Lab                      |   |   RAG Knowledge & Vector Engine    |  |
|  |  - 7-Dimensional Heuristic Quality Scorer                  |   |   - Recursive Markdown Chunker     |  |
|  |  - LLM-as-a-Judge Evaluation (G-Eval / MT-Bench)           |   |   - In-Memory / pgvector Retriever |  |
|  |  - Elo-style A/B Comparison Engine                         |   |   - Exact & Semantic Deduplicator  |  |
|  |  - Offline JSONL Test Harness & Benchmark Runner           |   +------------------------------------+  |
|  +------------------------------------------------------------+                                           |
|                                                                                                           |
|  +------------------------------------------------------------+   +------------------------------------+  |
|  |         Git-Like Prompt Version Control                    |   |   Data Engineering & Analytics     |  |
|  |  - Immutable Version Commits with Change Logs               |   |   - Pandas Aggregation Engine      |  |
|  |  - Line-by-line & Opcode Diff Computer                     |   |   - Latency Percentiles (p50-p99)  |  |
|  |  - Append-only Rollbacks (Restore)                         |   |   - Predictive Cost & Burn Model   |  |
|  +------------------------------------------------------------+   +------------------------------------+  |
+----------------------------------------------+------------------------------------------------------------+
                                               |
                                               v
+----------------------------------------------+------------------------------------------------------------+
|                                    Model Routing & Infrastructure Layer                                   |
|                                                                                                           |
|  +-----------------------------------------------------------------------------------------------------+  |
|  |                                      Model Router & Circuit Breaker                                  |  |
|  |   - Mock Provider (Zero-latency offline test harness)                                               |  |
|  |   - Google Gemini Provider (Gemini 1.5 Pro & Flash)                                                 |  |
|  |   - OpenAI Provider (GPT-4o, GPT-4o-mini)                                                           |  |
|  |   - Anthropic Provider (Claude 3.5 Sonnet)                                                          |  |
|  |   - Ollama Provider (Llama 3, Mistral, Local LLMs)                                                  |  |
|  +-----------------------------------------------------------------------------------------------------+  |
|                                                                                                           |
|  +------------------------------------+    +---------------------------------+    +--------------------+  |
|  |    SQLAlchemy 2.0 Async Storage    |    |   Redis Token Cache / Queue     |    |   NiceGUI / Plotly |  |
|  |    SQLite (Dev) / PostgreSQL (Prod)|    |   Distributed Session Broker    |    |   Glassmorphic UI  |  |
|  +------------------------------------+    +---------------------------------+    +--------------------+  |
+-----------------------------------------------------------------------------------------------------------+
```

---

## 3. Request Lifecycle

1. **Ingress & Correlation**:
   The request hits the ASGI server (Uvicorn). The context timing middleware injects a unique UUID `X-Request-ID` and begins the high-resolution execution timer.
2. **Security & Authentication Gate**:
   - The token bucket rate limiter validates quota based on IP address and user role.
   - For protected endpoints, the bearer JWT token is verified, and the user entity is queried with role authorization verified.
   - The prompt text is inspected by `InjectionGuard` for system instruction overrides, delimiter breaks, and sensitive PII.
3. **Domain Engine Dispatch**:
   The request is routed to the designated service (Prompt Generation Engine, Multi-Agent Orchestrator, Optimizer, Evaluator, or Library).
4. **Model Router & Resiliency**:
   Provider API calls are routed via `ModelRouter`. If an upstream API returns 5xx errors or timeouts, the circuit breaker opens, triggering graceful failover.
5. **Persistence & Telemetry**:
   Prompt snapshots are committed immutably. Analytics telemetry events record modality, model, tokens consumed, and latency.
6. **Egress Envelope**:
   The final payload is formatted inside a standardized `ResponseEnvelope[T]`, including process latency and metadata.
