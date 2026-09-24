# PromptForge AI - Production Deployment & Operations Guide

> **Module:** Infrastructure & Operations  
> **Environment:** Production Linux / Docker / Cloud Run / Kubernetes

---

## 1. Quick Start with Docker Compose

Deploy the complete stack (PromptForge AI + Redis + PostgreSQL) with a single command:

```bash
# 1. Clone repository
git clone https://github.com/enterprise/promptforge-ai.git
cd promptforge-ai

# 2. Configure production environment
cp .env.example .env
# Edit .env with your provider API keys and production SECRET_KEY

# 3. Launch stack
docker compose up -d --build

# 4. Verify running health status
docker compose ps
curl http://localhost:8000/health
```

The platform is immediately available at:
- **FastAPI REST API & Docs:** `http://localhost:8000/docs`
- **Interactive NiceGUI Dashboard:** `http://localhost:8000/ui`

---

## 2. Environment Variables Configuration

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Deployment stage (`development`, `staging`, `production`) |
| `DEBUG` | `false` | Enable verbose debug logging |
| `HOST` | `0.0.0.0` | Bind host address |
| `PORT` | `8000` | Application HTTP port |
| `SECRET_KEY` | *(Must be set)* | 32+ character cryptographic secret for JWT signing |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/promptforge.db` | Async SQLAlchemy database connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis cache and session broker |
| `GEMINI_API_KEY` | *(Optional)* | Google Gemini API key for production Gemini models |
| `OPENAI_API_KEY` | *(Optional)* | OpenAI API key for GPT-4o models |
| `ANTHROPIC_API_KEY` | *(Optional)* | Anthropic API key for Claude 3.5 Sonnet |
| `ENABLE_RAG` | `true` | Enable RAG knowledge vector store |
| `ENABLE_AGENTS` | `true` | Enable multi-agent orchestration pipeline |
| `ENABLE_PROMPT_INJECTION_DEFENSE` | `true` | Enable InjectionGuard and sandwiching defense |

---

## 3. Database Initialization & Seeding

The application automatically initializes database tables on startup. To explicitly seed default categories, models, and demo accounts via CLI:

```bash
# Running inside container or local virtualenv
promptforge seed-db
```

---

## 4. Health & Liveness Probes

PromptForge AI exposes high-availability probes for Kubernetes and container orchestrators:
- **Liveness / Readiness Probe:** `GET /health` (returns status, version, and active environment)
- **Detailed System Readiness:** `GET /api/v1/health/ready` (validates database connectivity and model router circuit breakers)
