# PromptForge AI 🚀

> **Generate. Optimize. Test. Evaluate. Deploy.**  
> *Production-Grade Enterprise AI Prompt Engineering, Evaluation, and Orchestration Platform.*

---

## 🌟 Overview

**PromptForge AI** is an advanced, production-ready AI Prompt Engineering and Evaluation platform designed to bridge the gap between simple chat wrappers and enterprise-grade generative AI systems. It empowers engineers, researchers, and creators to transform simple concepts into highly-structured, model-specific, and performance-evaluated prompts across diverse modalities (**Text, Image, Video, Audio, Code, Agent, Data, and Research**).

---

## 🏛️ System Architecture

PromptForge AI is built as a Python-first modular monolith with clean hexagonal separation:

```
                         PROMPTFORGE AI
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
             Python UI                 FastAPI API
             (NiceGUI)                       │
                                             │
                 ┌───────────────────────────┼──────────────────────┐
                 │                           │                      │
           Prompt Engine               AI Agent System         Evaluation
                 │                           │                      │
        ┌────────┼────────┐            ┌─────┼─────┐          ┌─────┼─────┐
        │        │        │            │     │     │          │     │     │
      Text     Image    Video       Planner RAG  Tools       Judge A/B   Tests
        │        │        │
        └────────┼────────┘
                 │
            Model Router
                 │
       ┌─────────┼─────────┐
       │         │         │
    Gemini    OpenAI     Ollama / Mock
       │
       ▼
   PostgreSQL + pgvector
       │
     Redis Cache
       │
    Async Workers & Analytics
```

---

## 🔑 Key Capabilities

- **Multimodal Prompt Generation**: Dedicated generation engines for Text, Image (Midjourney, SD, FLUX), Video (Runway, Sora, Kling), Audio, and Code.
- **Intent & Missing Information Extraction**: Automated entity extraction, slot filling, and clarification questions.
- **Audience & Child-Safe Filtering**: Context-aware vocabulary and strict safety guardrails.
- **Prompt Optimizer & Repair Engine**: Deep weakness analysis, before-and-after diffs, and iterative refinement.
- **AI-as-a-Judge Evaluation Lab**: Multi-dimensional scoring (Clarity, Specificity, Context, Safety, Format) with cost and latency tracking.
- **Git-like Prompt Version Control**: Track versions, restore checkpoints, compare diffs, and inspect evaluation history.
- **Multi-Model Router & Registry**: Agnostic provider integration (Gemini, OpenAI, Anthropic, Ollama, and offline Mock provider).
- **RAG Knowledge Base**: Vector embeddings + hybrid search over prompt engineering principles and guidelines.
- **Data Engineering & Analytics**: Event tracking, daily usage rollups, and interactive Plotly dashboards.
- **Production Guardrails**: Indirect prompt injection defense, secret sanitization, and Redis-backed rate limiting.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Virtual environment tool (`uv` recommended, or standard `venv`)

### 1. Setup Environment
```bash
# Clone and enter directory
cd "PromptForge AI"

# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies (development mode)
uv pip install -e ".[dev]"
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```

### 3. Run the CLI
```bash
# Verify CLI setup
python -m promptforge --help
```

---

## 📄 License
MIT License. See [LICENSE](file:///Users/maheshs/PromptForge%20AI/LICENSE) for details.
