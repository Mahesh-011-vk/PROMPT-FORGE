"""
PromptForge AI - Advanced Prompt Template Engine.

Provides regex-based and Jinja2-compatible variable parsing, validation,
and safe rendering for prompt templates with defaults, filters, and typing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TemplateVariable:
    """Metadata for an extracted template variable."""

    name: str
    required: bool = True
    default_value: str | None = None
    filters: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass
class TemplateRenderResult:
    """Result of rendering a template string with variable values."""

    rendered_text: str
    used_variables: dict[str, Any]
    missing_variables: list[str]
    success: bool
    error_message: str | None = None


class TemplateEngine:
    """Parses, inspects, and renders prompt templates containing {{var}} syntax."""

    # Matches {{ variable_name }}, {{ var | default: "val" }}, {{ var | upper }}
    VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)(?:\s*\|\s*([^}]+))?\s*\}\}")

    @classmethod
    def extract_variables(cls, template_str: str) -> list[TemplateVariable]:
        """Extract all variables, defaults, and filter chains from a template string."""
        seen: dict[str, TemplateVariable] = {}

        for match in cls.VAR_PATTERN.finditer(template_str):
            var_name = match.group(1).strip()
            filter_pipe = match.group(2)

            default_val: str | None = None
            filters: list[str] = []
            is_required = True

            if filter_pipe:
                parts = [p.strip() for p in filter_pipe.split("|")]
                for part in parts:
                    if part.startswith(("default:", "default=")):
                        # Extract default value (stripping optional quotes)
                        val = part.split(":", 1)[-1] if ":" in part else part.split("=", 1)[-1]
                        val = val.strip().strip("'\"")
                        default_val = val
                        is_required = False
                    elif part in {"upper", "lower", "trim", "capitalize", "title"}:
                        filters.append(part)
                    else:
                        # treat non-filter single string as default if not set
                        if default_val is None:
                            default_val = part.strip("'\"")
                            is_required = False

            if var_name not in seen:
                seen[var_name] = TemplateVariable(
                    name=var_name,
                    required=is_required,
                    default_value=default_val,
                    filters=filters,
                )
            else:
                # Merge if seen before with defaults
                existing = seen[var_name]
                if default_val is not None and existing.default_value is None:
                    existing.default_value = default_val
                    existing.required = False
                for flt in filters:
                    if flt not in existing.filters:
                        existing.filters.append(flt)

        return list(seen.values())

    @classmethod
    def render(
        cls,
        template_str: str,
        variables: dict[str, Any] | None = None,
        strict: bool = False,
    ) -> TemplateRenderResult:
        """Render a template string by substituting variables with optional filters.

        Args:
            template_str: The prompt template text.
            variables: Dictionary of variable values.
            strict: If True, raises or fails when a required variable is missing.

        Returns:
            TemplateRenderResult with rendered text and audit details.
        """
        variables = variables or {}
        extracted = cls.extract_variables(template_str)
        used_vars: dict[str, Any] = {}
        missing_vars: list[str] = []

        # Check for missing required variables
        for meta in extracted:
            if meta.name in variables:
                val = variables[meta.name]
                if val is None or (isinstance(val, str) and not val.strip() and meta.required):
                    if meta.default_value is not None:
                        used_vars[meta.name] = meta.default_value
                    elif meta.required:
                        missing_vars.append(meta.name)
                else:
                    used_vars[meta.name] = val
            elif meta.default_value is not None:
                used_vars[meta.name] = meta.default_value
            elif meta.required:
                missing_vars.append(meta.name)

        if strict and missing_vars:
            return TemplateRenderResult(
                rendered_text=template_str,
                used_variables=used_vars,
                missing_variables=missing_vars,
                success=False,
                error_message=f"Missing required template variables: {', '.join(missing_vars)}",
            )

        def replacer(match: re.Match) -> str:
            var_name = match.group(1).strip()
            filter_pipe = match.group(2)

            # Determine base value
            val = used_vars.get(var_name)
            if val is None:
                # Fallback to default in expression if available
                if filter_pipe:
                    for part in [p.strip() for p in filter_pipe.split("|")]:
                        if part.startswith(("default:", "default=")):
                            val = part.split(":", 1)[-1] if ":" in part else part.split("=", 1)[-1]
                            val = val.strip().strip("'\"")
                            break
                        elif part not in {"upper", "lower", "trim", "capitalize", "title"}:
                            val = part.strip("'\"")
                            break
                if val is None:
                    # Keep raw token if missing and not strict
                    return match.group(0)

            # Stringify value
            str_val = str(val)

            # Apply filters
            if filter_pipe:
                parts = [p.strip() for p in filter_pipe.split("|")]
                for part in parts:
                    if part == "upper":
                        str_val = str_val.upper()
                    elif part == "lower":
                        str_val = str_val.lower()
                    elif part == "trim":
                        str_val = str_val.strip()
                    elif part == "capitalize":
                        str_val = str_val.capitalize()
                    elif part == "title":
                        str_val = str_val.title()

            return str_val

        rendered = cls.VAR_PATTERN.sub(replacer, template_str)

        return TemplateRenderResult(
            rendered_text=rendered,
            used_variables=used_vars,
            missing_variables=missing_vars,
            success=len(missing_vars) == 0 or not strict,
            error_message=None if not missing_vars else f"Rendered with missing variables: {missing_vars}",
        )
