# ==============================================================================
# PromptForge AI - Production Multi-Stage Dockerfile
# "Generate. Optimize. Test. Evaluate. Deploy."
# ==============================================================================

# Stage 1: Builder Stage
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies for C-extensions (greenlet, bcrypt, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /build/venv
ENV PATH="/build/venv/bin:$PATH"

# Copy package specifications and source code (required by hatchling build backend)
COPY pyproject.toml /build/
COPY app /build/app
COPY promptforge /build/promptforge

# Install dependencies including full feature set
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[full]"

# ==============================================================================
# Stage 2: Production Distroless / Hardened Runtime Stage
# ==============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/venv/bin:$PATH" \
    PORT=8000 \
    HOST=0.0.0.0

# Install runtime utilities (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Security: Create unprivileged application user
RUN groupadd -g 10001 promptforge && \
    useradd -u 10001 -g promptforge -m -s /bin/bash promptforge

# Copy virtual environment from builder stage
COPY --from=builder /build/venv /app/venv

# Copy application source code and knowledge repositories
COPY --chown=promptforge:promptforge app /app/app
COPY --chown=promptforge:promptforge promptforge /app/promptforge
COPY --chown=promptforge:promptforge knowledge /app/knowledge
COPY --chown=promptforge:promptforge datasets /app/datasets
COPY --chown=promptforge:promptforge pyproject.toml /app/pyproject.toml
COPY --chown=promptforge:promptforge docker-entrypoint.sh /app/docker-entrypoint.sh

# Install local package metadata
RUN pip install --no-deps -e . && \
    chmod +x /app/docker-entrypoint.sh && \
    mkdir -p /app/data && \
    chown -R promptforge:promptforge /app

# Switch to unprivileged runtime user
USER promptforge

# Expose HTTP API & NiceGUI Port
EXPOSE 8000

# Container Healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --proxy-headers"]
