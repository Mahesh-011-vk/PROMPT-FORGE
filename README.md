# PromptForge AI 🚀

> **"Generate. Optimize. Test. Evaluate. Deploy."**  
> *Enterprise-Grade Autonomous AI Prompt Engineering, Evaluation, and Lifecycle Management Platform.*

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![NiceGUI](https://img.shields.io/badge/NiceGUI-2.0+-FF5722.svg)](https://nicegui.io)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.10+-E92063.svg)](https://pydantic.dev)
[![Test Suite](https://img.shields.io/badge/Tests-65%2F65%20Passed-brightgreen.svg)](tests/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff%200%20Errors-black.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Executive Overview

**PromptForge AI** is a production-grade enterprise platform designed to elevate prompt engineering from subjective guesswork into a deterministic, scientifically evaluated, and version-controlled software discipline.

Unlike basic chat wrappers, PromptForge AI provides a full-stack, hexagonal-architecture platform integrating:
- **Multimodal Prompt Synthesis**: Tailored compilers for Text, Image (Midjourney v6, SDXL, FLUX), Video (Runway Gen-3, Luma Dream Machine, Sora, Kling), Audio, and Code.
- **Autonomous Multi-Agent Orchestrator**: A 6-agent collaborative DAG (`Planner` ➔ `Intent` ➔ `Knowledge` ➔ `Builder` ➔ `Critic` ➔ `Safety`) that iteratively refines prompts with thought traces.
- **Diagnostic Optimizer & Repair Engine**: Detects missing dimensions, calculates quantitative score boosts, and rewrites broken or ambiguous prompts with before/after diffs.
- **7-Dimensional Heuristic Evaluation Lab**: Audits Clarity, Specificity, Context, Constraints, Output Format, Safety, and Ambiguity Control with LLM-as-a-judge and A/B benchmarking.
- **RAG Knowledge Base & Deduplication**: Markdown knowledge ingestion, dense semantic vector retrieval, cosine similarity indexing, and exact SHA-256 fingerprint deduplication.
- **Git-like Prompt Version Control**: Semantic versioning (`major.minor.patch`), visual diff calculation, commit messages, rollback, and branching.
- **Enterprise Security & Guardrails**: PII scrubbers (SSN, credit cards, emails, phones, IPs), injection defense, cryptographic nonce sandwich wrappers, and token-bucket rate limiters.
- **Data Engineering & Analytics**: Pandas-powered latency percentile computation (p50, p95, p99), token cost forecasting, and live Plotly visualization dashboards.
- **Python-First UI (NiceGUI)**: Sleek, dark-mode glassmorphic studio directly mounted on FastAPI at `/ui`.

---

## 🏛️ System Architecture

```
                                  PROMPTFORGE AI PLATFORM
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │                                           │
         Interactive NiceGUI Studio (port 8000/ui)      FastAPI REST API Gateway (/api/v1)
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             │
                   ┌─────────────────────────┼─────────────────────────┐
                   │                         │                         │
         Autonomous Multi-Agent     Prompt Generation        7-Dimensional Eval Lab
         Orchestrator (6 Agents)    & Optimizer Engine       & LLM-as-a-Judge
                   │                         │                         │
         ┌─────────┴─────────┐               │               ┌─────────┴─────────┐
         │ • PlannerAgent    │               │               │ • Heuristic Scorer│
         │ • IntentAgent     │               │               │ • LLM Judge       │
         │ • KnowledgeAgent  │               │               │ • A/B Matrix      │
         │ • BuilderAgent    │               │               │ • Offline Runner  │
         │ • CriticAgent     │               │               └───────────────────┘
         │ • SafetyAgent     │               │
         └───────────────────┘               ▼
                                   Multi-Model Provider Router
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       ▼                     ▼                     ▼
                  Google Gemini           OpenAI           Anthropic / Ollama / Mock
                       │                     │                     │
                       └─────────────────────┬─────────────────────┘
                                             │
                   ┌─────────────────────────┼─────────────────────────┐
                   ▼                         ▼                         ▼
         PostgreSQL + pgvector           Redis Cache         Data Engine & Analytics
         (SQLAlchemy 2.0 Async)      (Rate Limit / Nonces)   (Pandas / NumPy / Plotly)
```

---

## 🚀 Quickstart & Interactive Tour

### 1. Installation & Environment

```bash
# Clone the repository
git clone https://github.com/mahesh-s/promptforge-ai.git
cd "PromptForge AI"

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package and all dependencies in editable mode
pip install -e ".[dev]"
```

### 2. Run Interactive Recruiter Demo Walkthrough
Run the terminal walkthrough showcasing all 7 core subsystems in under 30 seconds:

```bash
python demo/walkthrough.py
# Or via CLI:
promptforge demo
```

### 3. Launch Server & Interactive Web Studio

```bash
promptforge serve --port 8000
```
- **Web UI Studio
- **Interactive Swagger Docs
- **ReDoc API Reference
- **Health Probes

---

## 💻 CLI Commands Reference

PromptForge AI features a first-class Typer & Rich CLI:

```bash
# System diagnostics and environment verification
promptforge doctor

# Generate an enterprise prompt for Midjourney / SDXL
promptforge generate "portrait of a cyberpunk hacker" --modality image

# Optimize and boost the quality of a sub-optimal prompt
promptforge optimize "doctor in hospital" --modality image

# Run 7-dimensional heuristic evaluation on a prompt
promptforge evaluate "Write an async rate limiter in Python" --modality code

# Ingest knowledge documents into RAG vector storage
promptforge ingest --path knowledge/

# Run offline benchmark evaluation dataset
promptforge benchmark --dataset datasets/image_prompts.jsonl

# Launch production API & UI server
promptforge serve --host 0.0.0.0 --port 8000
```

---

## 🧪 Comprehensive Quality Assurance

The codebase is tested with 65 end-to-end and unit test suites:

```bash
# Run full test suite
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run strict code linting and formatting
ruff check .
```

### Test Suite Summary:
- `tests/test_scaffolding.py`: Core metadata, enums, settings, and CLI registration (6 tests)
- `tests/test_config.py`: Configuration resolution, model pricing formulas, logging formatters (9 tests)
- `tests/test_database.py`: SQLAlchemy 2.0 async lifecycle, cascades, seeders (3 tests)
- `tests/test_api_core.py`: FastAPI gateway, headers, health probes, models registry (4 tests)
- `tests/test_prompt_engine.py`: Intent extraction, Image, Video, Kids, and Enterprise compilers (6 tests)
- `tests/test_llm_router.py`: Abstract LLM provider, mock execution, circuit breaker failover (4 tests)
- `tests/test_optimizer.py`: Weakness diagnostics, repairs, cross-language tag preservation (4 tests)
- `tests/test_evaluator.py`: 7D heuristics, LLM judge, A/B testing, offline benchmark runner (5 tests)
- `tests/test_rag.py`: Text chunker, vector ingestion, semantic and exact deduplication (4 tests)
- `tests/test_library_and_versioning.py`: Jinja2 variable extraction, library CRUD, Git version control (6 tests)
- `tests/test_analytics.py`: Pandas percentile aggregation, burn rate forecasting (3 tests)
- `tests/test_agents.py`: 6-agent collaborative synthesis DAG, safety interception (4 tests)
- `tests/test_auth_and_security.py`: PII scrubbing, injection detection, cryptographic nonces, rate limiter, RBAC (6 tests)
- `tests/test_e2e_workflow.py`: Complete cross-platform lifecycle integration test (1 test)

**Total: 65 passed, 0 failures, 100% clean.**

---

## 🐳 Docker & Production Deployment

PromptForge AI is containerized with a hardened multi-stage Dockerfile and full Docker Compose stack:

```bash
# Launch entire stack (App + Redis + PostgreSQL with pgvector)
docker compose up -d --build

# View container logs
docker compose logs -f app

# Run health check
curl http://localhost:8000/health
```

---

## 📚 Technical Documentation

Deep-dive architectural documentation is available in the `docs/` directory:
- [System Architecture](docs/architecture.md)
- [REST API Specification](docs/api.md)
- [AI Engine & Multi-Agent Pipeline](docs/ai-pipeline.md)
- [RAG & Vector Retrieval](docs/rag.md)
- [Evaluation Lab & Scoring](docs/evaluation.md)
- [Security & Prompt Injection Defense](docs/security.md)
- [Data Engineering & Analytics Pipeline](docs/data-pipeline.md)
- [Production Deployment Guide](docs/deployment.md)
- [Portfolio & Recruiter Case Study](PORTFOLIO.md)

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
