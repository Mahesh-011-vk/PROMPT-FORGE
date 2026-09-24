"""
PromptForge AI - RAG & Semantic Vector Search API Endpoints.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.rag.deduplicator import prompt_deduplicator
from app.rag.retriever import knowledge_retriever
from app.schemas.common import ResponseEnvelope

router = APIRouter(prefix="/rag", tags=["RAG & Knowledge Base"])


class SearchRequest(BaseModel):
    query: str = Field(..., description="Semantic search query")
    top_k: int = Field(default=4, ge=1, le=20)


class DeduplicateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt text to test for duplication")
    similarity_threshold: float = Field(default=0.92, ge=0.5, le=1.0)


@router.post("/ingest")
async def ingest_knowledge(
    directory: str = Query("knowledge", description="Directory of markdown documents to ingest"),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """
    Ingests markdown knowledge files into document chunks with dense vector embeddings.
    """
    chunks_created = await knowledge_retriever.ingest_directory(directory, db)
    return ResponseEnvelope(
        data={
            "status": "INGESTED",
            "directory": directory,
            "chunks_created": chunks_created,
        }
    )


@router.post("/search")
async def search_knowledge(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[dict]]:
    """
    Executes semantic vector similarity search over the knowledge base.
    """
    results = await knowledge_retriever.search(
        query=request.query,
        session=db,
        top_k=request.top_k,
    )
    return ResponseEnvelope(data=results)


@router.post("/deduplicate")
async def check_deduplication(
    request: DeduplicateRequest,
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[dict]:
    """
    Analyzes whether a prompt is an exact or near-duplicate of an existing prompt.
    """
    result = await prompt_deduplicator.check_duplicate(
        candidate_text=request.prompt,
        session=db,
        similarity_threshold=request.similarity_threshold,
    )
    return ResponseEnvelope(data=result)
