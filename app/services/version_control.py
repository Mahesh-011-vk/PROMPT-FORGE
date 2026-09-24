"""
PromptForge AI - Git-Like Version Control Service.

Implements immutable version snapshots, commit logs, semantic diff computation,
and git-style append-only rollbacks for prompts.
"""

from __future__ import annotations

import difflib
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException, ValidationException
from app.models.prompt import Prompt, PromptVersion
from app.schemas.versioning import (
    DiffChunk,
    VersionCommitRequest,
    VersionDiffResponse,
    VersionRestoreResponse,
    VersionSummary,
)


class VersionControlService:
    """Service implementing Git-like version control operations on prompts."""

    @classmethod
    async def commit_new_version(
        cls,
        db: AsyncSession,
        prompt_id: str,
        payload: VersionCommitRequest,
        author_id: str | None = None,
    ) -> VersionSummary:
        """Create a new version commit for an existing prompt and advance HEAD pointer."""
        stmt = select(Prompt).where(Prompt.id == prompt_id)
        res = await db.execute(stmt)
        prompt = res.scalars().first()
        if not prompt:
            raise ResourceNotFoundException("Prompt", prompt_id)

        # Get highest current version number
        num_stmt = select(func.coalesce(func.max(PromptVersion.version_number), 0)).where(
            PromptVersion.prompt_id == prompt_id
        )
        num_res = await db.execute(num_stmt)
        max_num = num_res.scalar() or 0
        new_version_number = max_num + 1

        new_version = PromptVersion(
            prompt_id=prompt_id,
            version_number=new_version_number,
            prompt_text=payload.prompt_text,
            negative_prompt=payload.negative_prompt,
            structured_spec=payload.structured_spec,
            variables=payload.variables,
            target_model=payload.target_model,
            quality_score=payload.quality_score,
            change_log=payload.change_log,
            author_id=author_id,
        )
        db.add(new_version)
        await db.flush()

        # Update prompt HEAD pointer
        prompt.current_version_id = new_version.id
        await db.commit()

        return VersionSummary(
            id=new_version.id,
            prompt_id=prompt_id,
            version_number=new_version.version_number,
            prompt_text=new_version.prompt_text,
            negative_prompt=new_version.negative_prompt,
            target_model=new_version.target_model,
            quality_score=new_version.quality_score,
            change_log=new_version.change_log,
            is_current=True,
            created_at=new_version.created_at.isoformat() if new_version.created_at else None,
        )

    @classmethod
    async def list_versions(
        cls,
        db: AsyncSession,
        prompt_id: str,
    ) -> list[VersionSummary]:
        """List version commit history for a prompt."""
        stmt = select(Prompt).where(Prompt.id == prompt_id)
        res = await db.execute(stmt)
        prompt = res.scalars().first()
        if not prompt:
            raise ResourceNotFoundException("Prompt", prompt_id)

        v_stmt = (
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
        )
        v_res = await db.execute(v_stmt)
        versions = v_res.scalars().all()

        return [
            VersionSummary(
                id=v.id,
                prompt_id=prompt_id,
                version_number=v.version_number,
                prompt_text=v.prompt_text,
                negative_prompt=v.negative_prompt,
                target_model=v.target_model,
                quality_score=v.quality_score,
                change_log=v.change_log,
                is_current=(v.id == prompt.current_version_id),
                created_at=v.created_at.isoformat() if v.created_at else None,
            )
            for v in versions
        ]

    @classmethod
    async def get_version(
        cls,
        db: AsyncSession,
        prompt_id: str,
        version_id_or_number: str | int,
    ) -> dict[str, Any]:
        """Retrieve a specific version snapshot."""
        stmt = select(PromptVersion).where(PromptVersion.prompt_id == prompt_id)
        if isinstance(version_id_or_number, int) or (isinstance(version_id_or_number, str) and version_id_or_number.isdigit()):
            stmt = stmt.where(PromptVersion.version_number == int(version_id_or_number))
        else:
            stmt = stmt.where(PromptVersion.id == str(version_id_or_number))

        res = await db.execute(stmt)
        version = res.scalars().first()
        if not version:
            raise ResourceNotFoundException("PromptVersion", str(version_id_or_number))

        return version.to_dict()

    @classmethod
    async def compute_diff(
        cls,
        db: AsyncSession,
        prompt_id: str,
        from_ver_num: int,
        to_ver_num: int,
    ) -> VersionDiffResponse:
        """Compute line-by-line and character diff between two version numbers."""
        stmt = select(PromptVersion).where(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version_number.in_([from_ver_num, to_ver_num]),
        )
        res = await db.execute(stmt)
        versions = res.scalars().all()

        v_map = {v.version_number: v for v in versions}
        if from_ver_num not in v_map:
            raise ValidationException(f"Source version v{from_ver_num} not found on prompt")
        if to_ver_num not in v_map:
            raise ValidationException(f"Target version v{to_ver_num} not found on prompt")

        v_from = v_map[from_ver_num]
        v_to = v_map[to_ver_num]

        lines_from = v_from.prompt_text.splitlines()
        lines_to = v_to.prompt_text.splitlines()

        # Compute unified diff string
        unified = "\n".join(
            difflib.unified_diff(
                lines_from,
                lines_to,
                fromfile=f"v{from_ver_num}",
                tofile=f"v{to_ver_num}",
                lineterm="",
            )
        )

        # Compute line-by-line chunks
        matcher = difflib.SequenceMatcher(None, lines_from, lines_to)
        similarity = round(matcher.ratio(), 4)

        chunks: list[DiffChunk] = []
        additions = 0
        deletions = 0
        unchanged = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for idx, line in enumerate(lines_from[i1:i2]):
                    chunks.append(
                        DiffChunk(
                            type="unchanged",
                            content=line,
                            line_number_from=i1 + idx + 1,
                            line_number_to=j1 + idx + 1,
                        )
                    )
                    unchanged += 1
            elif tag == "replace":
                for idx, line in enumerate(lines_from[i1:i2]):
                    chunks.append(
                        DiffChunk(
                            type="removed",
                            content=line,
                            line_number_from=i1 + idx + 1,
                            line_number_to=None,
                        )
                    )
                    deletions += 1
                for idx, line in enumerate(lines_to[j1:j2]):
                    chunks.append(
                        DiffChunk(
                            type="added",
                            content=line,
                            line_number_from=None,
                            line_number_to=j1 + idx + 1,
                        )
                    )
                    additions += 1
            elif tag == "delete":
                for idx, line in enumerate(lines_from[i1:i2]):
                    chunks.append(
                        DiffChunk(
                            type="removed",
                            content=line,
                            line_number_from=i1 + idx + 1,
                            line_number_to=None,
                        )
                    )
                    deletions += 1
            elif tag == "insert":
                for idx, line in enumerate(lines_to[j1:j2]):
                    chunks.append(
                        DiffChunk(
                            type="added",
                            content=line,
                            line_number_from=None,
                            line_number_to=j1 + idx + 1,
                        )
                    )
                    additions += 1

        return VersionDiffResponse(
            from_version=from_ver_num,
            to_version=to_ver_num,
            from_version_id=v_from.id,
            to_version_id=v_to.id,
            additions_count=additions,
            deletions_count=deletions,
            unchanged_count=unchanged,
            similarity_ratio=similarity,
            unified_diff=unified,
            chunks=chunks,
        )

    @classmethod
    async def restore_version(
        cls,
        db: AsyncSession,
        prompt_id: str,
        target_version_number: int,
        author_id: str | None = None,
    ) -> VersionRestoreResponse:
        """Git-style rollback: commits a new latest version with content from target historical version."""
        stmt = select(Prompt).where(Prompt.id == prompt_id)
        res = await db.execute(stmt)
        prompt = res.scalars().first()
        if not prompt:
            raise ResourceNotFoundException("Prompt", prompt_id)

        target_stmt = select(PromptVersion).where(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version_number == target_version_number,
        )
        target_res = await db.execute(target_stmt)
        target_ver = target_res.scalars().first()
        if not target_ver:
            raise ResourceNotFoundException("PromptVersion", f"v{target_version_number}")

        # Determine new version number
        num_stmt = select(func.coalesce(func.max(PromptVersion.version_number), 0)).where(
            PromptVersion.prompt_id == prompt_id
        )
        max_num = (await db.execute(num_stmt)).scalar() or 0
        new_version_num = max_num + 1

        revert_version = PromptVersion(
            prompt_id=prompt_id,
            version_number=new_version_num,
            prompt_text=target_ver.prompt_text,
            negative_prompt=target_ver.negative_prompt,
            structured_spec=target_ver.structured_spec,
            variables=target_ver.variables,
            target_model=target_ver.target_model,
            quality_score=target_ver.quality_score,
            change_log=f"Rollback to version v{target_version_number}: {target_ver.change_log}",
            author_id=author_id,
        )
        db.add(revert_version)
        await db.flush()

        prompt.current_version_id = revert_version.id
        await db.commit()

        return VersionRestoreResponse(
            prompt_id=prompt_id,
            restored_from_version=target_version_number,
            new_version_number=new_version_num,
            new_version_id=revert_version.id,
            message=f"Successfully restored prompt to historical version v{target_version_number} as v{new_version_num}",
        )
