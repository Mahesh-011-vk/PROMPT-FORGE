"""
PromptForge AI - RAG Knowledge Base Retriever & Ingestion Engine.

Provides vector similarity search and document ingestion across knowledge repositories.
"""

import math
import os

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.llm.router import model_router
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.rag.chunker import text_chunker


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calculates cosine similarity between two dense float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class KnowledgeRetriever:
    """Vector and hybrid search interface over stored domain knowledge."""

    async def ingest_directory(self, dir_path: str, session: AsyncSession) -> int:
        """
        Ingests all markdown documents from a directory into KnowledgeDocument and KnowledgeChunk tables.
        """
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory '{dir_path}' does not exist.")

        files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(".md")]
        total_chunks = 0

        for file_path in files:
            title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()
            async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
                content = await f.read()

            # Check if document already exists
            existing = (
                await session.execute(
                    select(KnowledgeDocument).where(KnowledgeDocument.title == title)
                )
            ).scalars().first()

            if existing:
                doc = existing
                doc.content = content
            else:
                doc = KnowledgeDocument(
                    title=title,
                    category="guidelines",
                    content=content,
                    metadata_={"file_path": file_path},
                )
                session.add(doc)
                await session.flush()

            # Split into chunks and generate embeddings
            raw_chunks = text_chunker.split_text(content)
            for idx, chunk_text in enumerate(raw_chunks):
                embedding = await model_router.embed(chunk_text)
                chunk = KnowledgeChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    embedding=embedding,
                )
                session.add(chunk)
                total_chunks += 1

        await session.commit()
        logger.info(f"Ingested {len(files)} documents with {total_chunks} vector chunks.")
        return total_chunks

    async def search(
        self,
        query: str,
        session: AsyncSession | None = None,
        top_k: int = 4,
        min_similarity: float = -1.0,
    ) -> list[dict]:
        """
        Executes semantic vector similarity search against knowledge chunks.
        """
        if session is None:
            from app.core.database import async_session_factory
            async with async_session_factory() as sess:
                return await self.search(query, session=sess, top_k=top_k, min_similarity=min_similarity)
        query_vector = await model_router.embed(query)
        chunks = (await session.execute(select(KnowledgeChunk))).scalars().all()

        scored_results = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            sim = cosine_similarity(query_vector, chunk.embedding)
            if sim >= min_similarity:
                scored_results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.chunk_text,
                    "similarity": round(sim, 4),
                })

        # Sort descending by similarity
        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:top_k]


knowledge_retriever = KnowledgeRetriever()
