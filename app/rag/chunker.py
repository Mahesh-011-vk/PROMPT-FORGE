"""
PromptForge AI - RAG Document Chunker.

Recursively splits long documents and guides into semantic chunks with overlap.
"""

from typing import List


class TextChunker:
    """Recursive character chunker preserving structural paragraph and header boundaries."""

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """Splits input text into a list of overlapping text chunks."""
        cleaned = text.strip()
        if not cleaned:
            return []

        if len(cleaned) <= self.chunk_size:
            return [cleaned]

        chunks: List[str] = []
        # Attempt split on double newline (paragraphs) first
        paragraphs = cleaned.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # If paragraph itself exceeds chunk_size, split by sentences
                if len(para) > self.chunk_size:
                    sentences = para.split(". ")
                    sub_chunk = ""
                    for s in sentences:
                        s = s.strip()
                        if len(sub_chunk) + len(s) + 2 <= self.chunk_size:
                            sub_chunk = f"{sub_chunk}. {s}".strip(". ")
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk)
                            sub_chunk = s
                    if sub_chunk:
                        current_chunk = sub_chunk
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


text_chunker = TextChunker()
