"""
Tests for Phase 12 (Prompt Library & Template System) and Phase 13 (Git-Like Version Control).
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.prompts.template_engine import TemplateEngine


def test_template_variable_extraction_and_filters():
    """Verify template variable extraction, defaults, and filter detection."""
    template = (
        "A photo of a {{subject}}, lighting is {{lighting | default: golden hour}}, "
        "shot on {{camera | default='Arri Alexa'}}, style is {{style | upper}}."
    )
    vars_list = TemplateEngine.extract_variables(template)
    var_dict = {v.name: v for v in vars_list}

    assert "subject" in var_dict
    assert var_dict["subject"].required is True
    assert var_dict["subject"].default_value is None

    assert "lighting" in var_dict
    assert var_dict["lighting"].required is False
    assert var_dict["lighting"].default_value == "golden hour"

    assert "camera" in var_dict
    assert var_dict["camera"].default_value == "Arri Alexa"

    assert "style" in var_dict
    assert "upper" in var_dict["style"].filters


def test_template_rendering_with_substitutions_and_filters():
    """Verify rendering with variable overrides and string filters."""
    template = "Portrait of {{role | capitalize}}, in {{location | upper}}, with {{mood | default: calm}} demeanor."
    res = TemplateEngine.render(
        template,
        variables={"role": "cyberpunk detective", "location": "neo tokyo"},
    )
    assert res.success is True
    assert "Cyberpunk detective" in res.rendered_text
    assert "NEO TOKYO" in res.rendered_text
    assert "calm" in res.rendered_text


def test_template_strict_rendering_missing_variable():
    """Verify strict mode fails when required variable is missing."""
    template = "Action scene of {{hero}} fighting in {{arena}}."
    res = TemplateEngine.render(template, variables={"hero": "Batman"}, strict=True)
    assert res.success is False
    assert "arena" in res.missing_variables


@pytest.mark.asyncio
async def test_api_template_endpoints():
    """Test template creation, variable extraction, and rendering via API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Extract variables endpoint
        ext_res = await client.post(
            "/api/v1/templates/extract-variables",
            json={"template_str": "Hero: {{name}}, Weapon: {{weapon | default: laser sword}}"},
        )
        assert ext_res.status_code == 200
        ext_data = ext_res.json()["data"]
        assert ext_data["count"] == 2

        # Create template endpoint
        tmpl_res = await client.post(
            "/api/v1/templates",
            json={
                "title": "Fantasy Lore Generator",
                "description": "Epic fantasy lore template",
                "modality": "text",
                "category": "creative",
                "template_str": "Tell the tale of {{kingdom}} ruled by {{ruler | default: King Arthur}}.",
                "default_variables": {"kingdom": "Avalon"},
            },
        )
        assert tmpl_res.status_code == 200
        tmpl_id = tmpl_res.json()["data"]["id"]

        # Render template endpoint with database template_id
        render_res = await client.post(
            "/api/v1/templates/render",
            json={
                "template_id": tmpl_id,
                "variables": {"ruler": "Queen Guinevere"},
            },
        )
        assert render_res.status_code == 200
        rendered = render_res.json()["data"]["rendered_text"]
        assert "Avalon" in rendered
        assert "Queen Guinevere" in rendered


@pytest.mark.asyncio
async def test_api_library_crud_and_export_import():
    """Test prompt library CRUD, tagging, export, and import."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create prompt
        create_res = await client.post(
            "/api/v1/library/prompts",
            json={
                "title": "Quantum Computing Explainer",
                "raw_input": "Explain quantum computing to high schoolers",
                "prompt_text": "You are a quantum physicist. Explain qubits using a spinning coin analogy.",
                "modality": "text",
                "category": "education",
                "audience": "general",
                "target_model": "gpt-4o",
                "tags": ["physics", "quantum", "stem"],
                "is_favorite": True,
                "quality_score": 9.2,
            },
        )
        assert create_res.status_code == 200
        prompt_id = create_res.json()["data"]["id"]

        # Get prompt
        get_res = await client.post(
            "/api/v1/library/prompts",
            json={
                "title": "Second Prompt for Search",
                "raw_input": "Prompt test search",
                "prompt_text": "Another test prompt",
                "modality": "image",
                "category": "art",
                "tags": ["art"],
            },
        )
        assert get_res.status_code == 200

        # List prompts
        list_res = await client.get("/api/v1/library/prompts?q=Quantum")
        assert list_res.status_code == 200
        assert list_res.json()["total"] >= 1

        # List tags
        tags_res = await client.get("/api/v1/library/tags")
        assert tags_res.status_code == 200
        assert "physics" in tags_res.json()["data"]

        # Update prompt
        up_res = await client.put(
            f"/api/v1/library/prompts/{prompt_id}",
            json={"title": "Updated Quantum Computing Explainer", "is_favorite": False},
        )
        assert up_res.status_code == 200
        assert up_res.json()["data"]["title"] == "Updated Quantum Computing Explainer"
        assert up_res.json()["data"]["is_favorite"] is False

        # Export prompts to JSON
        exp_res = await client.post(
            "/api/v1/library/export",
            json={"format": "json"},
        )
        assert exp_res.status_code == 200
        assert exp_res.json()["data"]["format"] == "json"
        assert exp_res.json()["data"]["prompt_count"] >= 1

        # Export prompts to Markdown
        exp_md_res = await client.post(
            "/api/v1/library/export",
            json={"format": "markdown"},
        )
        assert exp_md_res.status_code == 200
        assert "# PromptForge AI" in exp_md_res.json()["data"]["content"]

        # Batch import prompts
        imp_res = await client.post(
            "/api/v1/library/import",
            json={
                "prompts": [
                    {
                        "title": "Imported Test Prompt",
                        "raw_input": "Import raw test",
                        "prompt_text": "Imported prompt content for testing",
                        "modality": "text",
                        "category": "marketing",
                        "tags": ["test-import"],
                    }
                ]
            },
        )
        assert imp_res.status_code == 200
        assert imp_res.json()["data"]["imported_count"] == 1


@pytest.mark.asyncio
async def test_api_version_control_workflow():
    """Test git-like commit, diff, and rollback on prompts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a prompt (automatically creates version 1)
        p_res = await client.post(
            "/api/v1/library/prompts",
            json={
                "title": "SaaS Landing Page Copy",
                "raw_input": "Write headline and subheadline for AI CRM",
                "prompt_text": "Write a high-converting headline for an AI CRM.\nInclude 3 key bullet points.",
                "modality": "text",
                "category": "marketing",
            },
        )
        prompt_id = p_res.json()["data"]["id"]

        # 2. Commit Version 2
        v2_res = await client.post(
            f"/api/v1/prompts/{prompt_id}/versions",
            json={
                "prompt_text": "Write a high-converting headline for an AI CRM.\nInclude 3 key bullet points.\nAdd a strong Call To Action button copy.",
                "change_log": "Added Call To Action instruction",
                "target_model": "gpt-4o",
                "quality_score": 8.8,
            },
        )
        assert v2_res.status_code == 200
        assert v2_res.json()["data"]["version_number"] == 2
        assert v2_res.json()["data"]["is_current"] is True

        # 3. List version history
        hist_res = await client.get(f"/api/v1/prompts/{prompt_id}/versions")
        assert hist_res.status_code == 200
        versions = hist_res.json()["data"]
        assert len(versions) == 2
        assert versions[0]["version_number"] == 2

        # 4. Compute diff between v1 and v2
        diff_res = await client.get(f"/api/v1/prompts/{prompt_id}/diff?from_version=1&to_version=2")
        assert diff_res.status_code == 200
        diff_data = diff_res.json()["data"]
        assert diff_data["additions_count"] >= 1
        assert diff_data["from_version"] == 1
        assert diff_data["to_version"] == 2
        assert "Call To Action" in diff_data["unified_diff"]

        # 5. Restore back to version 1
        restore_res = await client.post(f"/api/v1/prompts/{prompt_id}/restore/1")
        assert restore_res.status_code == 200
        restore_data = restore_res.json()["data"]
        assert restore_data["restored_from_version"] == 1
        assert restore_data["new_version_number"] == 3

        # 6. Verify prompt detail now has HEAD at version 3
        detail_res = await client.get(f"/api/v1/library/prompts/{prompt_id}")
        assert detail_res.status_code == 200
        assert len(detail_res.json()["data"]["versions"]) == 3
        assert detail_res.json()["data"]["versions"][0]["version_number"] == 3
