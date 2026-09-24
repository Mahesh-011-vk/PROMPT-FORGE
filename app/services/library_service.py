"""
PromptForge AI - Prompt Library Service.

Handles persistence, indexing, search, filtering, tagging, and import/export
of prompts and templates across multiple formats (JSON, CSV, Markdown, YAML).
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any
import yaml
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ResourceNotFoundException
from app.models.prompt import Prompt, PromptTemplate, PromptVersion
from app.models.user import User
from app.schemas.library import (
    PromptCreateRequest,
    PromptExportResponse,
    PromptImportItem,
    PromptUpdateRequest,
)


class LibraryService:
    """Service layer for prompt library management and format conversion."""

    @staticmethod
    async def get_or_create_default_user(db: AsyncSession) -> str:
        """Helper to get an existing user id or create a system demo user."""
        stmt = select(User.id).limit(1)
        res = await db.execute(stmt)
        user_id = res.scalar_one_or_none()
        if not user_id:
            user = User(
                email="system@promptforge.local",
                username="system_user",
                hashed_password="system_placeholder_hash",
                full_name="System Default",
            )
            db.add(user)
            await db.flush()
            user_id = user.id
        return user_id

    @classmethod
    async def list_prompts(
        cls,
        db: AsyncSession,
        query: str | None = None,
        modality: str | None = None,
        category: str | None = None,
        tag: str | None = None,
        is_favorite: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search and list prompts with filters."""
        stmt = select(Prompt).options(selectinload(Prompt.versions))

        if modality:
            stmt = stmt.where(Prompt.modality == modality)
        if category:
            stmt = stmt.where(Prompt.category == category)
        if is_favorite is not None:
            stmt = stmt.where(Prompt.is_favorite == is_favorite)
        if query:
            pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Prompt.title.ilike(pattern),
                    Prompt.raw_input.ilike(pattern),
                )
            )

        # Count query
        count_stmt = select(func.count(Prompt.id))
        if modality:
            count_stmt = count_stmt.where(Prompt.modality == modality)
        if category:
            count_stmt = count_stmt.where(Prompt.category == category)
        if is_favorite is not None:
            count_stmt = count_stmt.where(Prompt.is_favorite == is_favorite)
        if query:
            pattern = f"%{query}%"
            count_stmt = count_stmt.where(
                or_(
                    Prompt.title.ilike(pattern),
                    Prompt.raw_input.ilike(pattern),
                )
            )

        count_res = await db.execute(count_stmt)
        total_count = count_res.scalar() or 0

        stmt = stmt.order_by(Prompt.updated_at.desc()).limit(limit).offset(offset)
        result = await db.execute(stmt)
        prompts = result.scalars().all()

        output: list[dict[str, Any]] = []
        for p in prompts:
            # Filter by tag in python if tag provided
            if tag and tag not in (p.tags or []):
                continue

            current_ver_text = ""
            score = 0.0
            if p.versions:
                current_ver = next((v for v in p.versions if v.id == p.current_version_id), p.versions[-1])
                current_ver_text = current_ver.prompt_text
                score = current_ver.quality_score

            output.append({
                "id": p.id,
                "title": p.title,
                "raw_input": p.raw_input,
                "modality": p.modality,
                "category": p.category,
                "audience": p.audience,
                "is_favorite": p.is_favorite,
                "tags": p.tags or [],
                "current_version_id": p.current_version_id,
                "current_prompt_text": current_ver_text,
                "quality_score": score,
                "version_count": len(p.versions),
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            })

        return output, total_count

    @classmethod
    async def get_prompt(cls, db: AsyncSession, prompt_id: str) -> dict[str, Any]:
        """Fetch prompt detail including all versions."""
        stmt = (
            select(Prompt)
            .options(selectinload(Prompt.versions))
            .where(Prompt.id == prompt_id)
        )
        result = await db.execute(stmt)
        prompt = result.scalars().first()
        if not prompt:
            raise ResourceNotFoundException("Prompt", prompt_id)

        versions_data = [
            {
                "id": v.id,
                "version_number": v.version_number,
                "prompt_text": v.prompt_text,
                "negative_prompt": v.negative_prompt,
                "target_model": v.target_model,
                "quality_score": v.quality_score,
                "change_log": v.change_log,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in sorted(prompt.versions, key=lambda x: x.version_number, reverse=True)
        ]

        current_ver_text = ""
        score = 0.0
        if prompt.versions:
            current_ver = next(
                (v for v in prompt.versions if v.id == prompt.current_version_id),
                prompt.versions[-1],
            )
            current_ver_text = current_ver.prompt_text
            score = current_ver.quality_score

        return {
            "id": prompt.id,
            "title": prompt.title,
            "raw_input": prompt.raw_input,
            "modality": prompt.modality,
            "category": prompt.category,
            "audience": prompt.audience,
            "is_favorite": prompt.is_favorite,
            "tags": prompt.tags or [],
            "current_version_id": prompt.current_version_id,
            "current_prompt_text": current_ver_text,
            "quality_score": score,
            "versions": versions_data,
            "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
            "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
        }

    @classmethod
    async def create_prompt(
        cls,
        db: AsyncSession,
        payload: PromptCreateRequest,
    ) -> dict[str, Any]:
        """Create a new prompt and initialize version 1."""
        user_id = payload.user_id
        if not user_id:
            user_id = await cls.get_or_create_default_user(db)

        prompt = Prompt(
            project_id=payload.project_id,
            user_id=user_id,
            title=payload.title,
            raw_input=payload.raw_input,
            modality=payload.modality,
            category=payload.category,
            audience=payload.audience,
            is_favorite=payload.is_favorite,
            tags=payload.tags,
        )
        db.add(prompt)
        await db.flush()

        # Create Version 1
        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            prompt_text=payload.prompt_text,
            negative_prompt=payload.negative_prompt,
            structured_spec=payload.structured_spec,
            variables=payload.variables,
            target_model=payload.target_model,
            quality_score=payload.quality_score,
            change_log="Initial version creation",
            author_id=user_id,
        )
        db.add(version)
        await db.flush()

        prompt.current_version_id = version.id
        await db.commit()

        return await cls.get_prompt(db, prompt.id)

    @classmethod
    async def update_prompt(
        cls,
        db: AsyncSession,
        prompt_id: str,
        payload: PromptUpdateRequest,
    ) -> dict[str, Any]:
        """Update mutable metadata of a prompt."""
        stmt = select(Prompt).where(Prompt.id == prompt_id)
        result = await db.execute(stmt)
        prompt = result.scalars().first()
        if not prompt:
            raise ResourceNotFoundException("Prompt", prompt_id)

        if payload.title is not None:
            prompt.title = payload.title
        if payload.category is not None:
            prompt.category = payload.category
        if payload.audience is not None:
            prompt.audience = payload.audience
        if payload.tags is not None:
            prompt.tags = payload.tags
        if payload.is_favorite is not None:
            prompt.is_favorite = payload.is_favorite

        await db.commit()
        return await cls.get_prompt(db, prompt.id)

    @classmethod
    async def delete_prompt(cls, db: AsyncSession, prompt_id: str) -> bool:
        """Delete prompt and cascade versions."""
        stmt = select(Prompt).where(Prompt.id == prompt_id)
        result = await db.execute(stmt)
        prompt = result.scalars().first()
        if not prompt:
            raise ResourceNotFoundException("Prompt", prompt_id)

        await db.delete(prompt)
        await db.commit()
        return True

    @classmethod
    async def list_unique_tags(cls, db: AsyncSession) -> list[str]:
        """Collect all unique tags across the library."""
        stmt = select(Prompt.tags)
        result = await db.execute(stmt)
        all_tags = set()
        for tags in result.scalars().all():
            if isinstance(tags, list):
                for t in tags:
                    if t:
                        all_tags.add(t.strip().lower())
        return sorted(all_tags)

    @classmethod
    async def export_prompts(
        cls,
        db: AsyncSession,
        format_type: str = "json",
        modality: str | None = None,
        category: str | None = None,
        tag: str | None = None,
        only_favorites: bool = False,
    ) -> PromptExportResponse:
        """Export library prompts into JSON, CSV, Markdown, or YAML format."""
        prompts, _ = await cls.list_prompts(
            db=db,
            modality=modality,
            category=category,
            tag=tag,
            is_favorite=True if only_favorites else None,
            limit=1000,
        )

        content: str
        filename: str

        if format_type == "json":
            content = json.dumps(prompts, indent=2, default=str)
            filename = "promptforge_library_export.json"

        elif format_type == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["id", "title", "modality", "category", "prompt_text", "tags", "quality_score", "is_favorite"])
            for p in prompts:
                writer.writerow([
                    p.get("id"),
                    p.get("title"),
                    p.get("modality"),
                    p.get("category"),
                    p.get("current_prompt_text"),
                    ",".join(p.get("tags", [])),
                    p.get("quality_score"),
                    p.get("is_favorite"),
                ])
            content = output.getvalue()
            filename = "promptforge_library_export.csv"

        elif format_type == "markdown":
            lines = ["# PromptForge AI - Exported Prompt Library\n\n"]
            for p in prompts:
                fav = "★ " if p.get("is_favorite") else ""
                lines.append(f"## {fav}{p.get('title')}\n")
                lines.append(f"- **Modality:** `{p.get('modality')}` | **Category:** `{p.get('category')}`")
                lines.append(f"- **Quality Score:** `{p.get('quality_score')}/10`")
                lines.append(f"- **Tags:** {', '.join(p.get('tags', []))}\n")
                lines.append("```text")
                lines.append(p.get("current_prompt_text", ""))
                lines.append("```\n---\n")
            content = "\n".join(lines)
            filename = "promptforge_library_export.md"

        elif format_type == "yaml":
            content = yaml.dump(prompts, sort_keys=False)
            filename = "promptforge_library_export.yaml"

        else:
            raise ValueError(f"Unsupported export format: {format_type}")

        return PromptExportResponse(
            format=format_type,
            content=content,
            prompt_count=len(prompts),
            filename=filename,
        )

    @classmethod
    async def import_prompts(
        cls,
        db: AsyncSession,
        items: list[PromptImportItem],
    ) -> tuple[int, list[str], list[str]]:
        """Import prompts in batch."""
        user_id = await cls.get_or_create_default_user(db)
        created_ids: list[str] = []
        errors: list[str] = []

        for item in items:
            try:
                prompt = Prompt(
                    user_id=user_id,
                    title=item.title,
                    raw_input=item.raw_input,
                    modality=item.modality,
                    category=item.category,
                    audience=item.audience,
                    tags=item.tags,
                )
                db.add(prompt)
                await db.flush()

                version = PromptVersion(
                    prompt_id=prompt.id,
                    version_number=1,
                    prompt_text=item.prompt_text,
                    target_model=item.target_model,
                    quality_score=item.quality_score,
                    change_log="Batch imported prompt",
                    author_id=user_id,
                )
                db.add(version)
                await db.flush()

                prompt.current_version_id = version.id
                created_ids.append(prompt.id)
            except Exception as e:
                errors.append(f"Failed to import '{item.title}': {str(e)}")

        await db.commit()
        return len(created_ids), created_ids, errors
