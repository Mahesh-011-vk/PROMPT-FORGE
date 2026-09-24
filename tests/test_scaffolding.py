"""
Phase 1 Scaffolding and Verification Tests.
Tests package initialization, configuration loading, CLI commands, and directory structure.
"""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app import __app_name__, __tagline__, __version__
from app.cli import app as cli_app
from app.config.constants import AudienceCategory, Environment, Modality, ProviderType
from app.config.settings import settings
from app.main import app as fastapi_app


def test_package_metadata():
    """Verify package metadata and constants."""
    assert __version__ == "0.1.0"
    assert __app_name__ == "PromptForge AI"
    assert "Generate. Optimize. Test. Evaluate. Deploy." in __tagline__


def test_settings_defaults():
    """Verify default application settings."""
    assert settings.APP_NAME == "PromptForge AI"
    assert settings.ENVIRONMENT == Environment.DEVELOPMENT
    assert settings.DEMO_MODE is True
    assert settings.DEFAULT_PROVIDER == "mock"
    assert settings.API_V1_PREFIX == "/api/v1"


def test_constants_enums():
    """Verify core domain taxonomy enums."""
    assert Modality.TEXT.value == "text"
    assert Modality.IMAGE.value == "image"
    assert Modality.VIDEO.value == "video"
    assert AudienceCategory.KIDS.value == "kids"
    assert AudienceCategory.ADULTS.value == "adults"
    assert ProviderType.MOCK.value == "mock"


def test_cli_commands_registered():
    """Verify Typer CLI commands are properly registered using CliRunner."""
    from typer.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    expected_commands = [
        "version",
        "generate",
        "optimize",
        "evaluate",
        "ingest",
        "benchmark",
        "worker",
        "serve",
    ]
    for cmd in expected_commands:
        assert cmd in result.output, f"Command '{cmd}' not found in CLI help output"

    # Test version command output specifically
    version_result = runner.invoke(cli_app, ["version"])
    assert version_result.exit_code == 0
    assert "PromptForge AI" in version_result.output



def test_directory_hierarchy_exists():
    """Verify expected folder structure exists on the filesystem."""
    required_dirs = [
        "app/config",
        "app/core",
        "app/models",
        "app/schemas",
        "app/api/v1",
        "app/services",
        "app/prompts",
        "app/llm",
        "app/rag",
        "app/agents",
        "app/evaluators",
        "app/security",
        "app/analytics",
        "app/workers",
        "app/ui",
        "tests",
        "datasets",
        "knowledge",
        "docs",
        "docker",
    ]
    for directory in required_dirs:
        assert os.path.isdir(directory), f"Required directory '{directory}' does not exist"


@pytest.mark.asyncio
async def test_fastapi_health_endpoint():
    """Verify FastAPI baseline health endpoint returns 200 OK."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "PromptForge AI"
        assert data["demo_mode"] is True
