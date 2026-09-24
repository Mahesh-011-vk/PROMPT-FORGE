#!/bin/bash
set -e

# ==============================================================================
# PromptForge AI - Container Entrypoint Script
# ==============================================================================

echo "=================================================================="
echo "⚡ Starting PromptForge AI Container Runtime"
echo "Tagline: Generate. Optimize. Test. Evaluate. Deploy."
echo "=================================================================="

# Ensure data directory exists with write permissions
mkdir -p /app/data

# If database seeding or initialization CLI is requested
if [ "$1" = "seed" ]; then
    echo "🌱 Executing database seed..."
    exec python -m app.cli seed-db
fi

# Execute passed command (defaults to uvicorn)
exec "$@"
