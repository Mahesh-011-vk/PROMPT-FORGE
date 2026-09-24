# PromptForge AI - RAG & Vector Knowledge Engine

> **Module:** `app.rag`  
> **Role:** Retrieval-Augmented Generation, Semantic Search, and Deduplication

---

## 1. Knowledge Base Repository

The RAG engine indexes authoritative prompt engineering guides located in `/knowledge`:
- `prompt_engineering_principles.md`: Core system directives, role framing, and constraint design.
- `image_prompting_guide.md`: Optics, camera focal lengths, volumetric illumination, rendering engines.
- `video_prompting_guide.md`: Camera trajectories, temporal continuity, and motion parameters.
- `code_prompting_standards.md`: Architecture specification, test generation, and anti-hallucination tactics.

---

## 2. Text Chunker Architecture

The chunker splits long markdown documentation hierarchically while preserving semantic context:
1. **Splitting Hierarchy:** Splits sequentially on double newlines (`\n\n`), single newlines (`\n`), periods (`. `), and whitespace spaces (` `).
2. **Chunk Size & Overlap:** Default chunk size is **400 characters** with an overlap of **60 characters**, ensuring cross-boundary sentences are not split awkwardly.
3. **Metadata Preservation:** Each chunk records `document_id`, `chunk_index`, and character byte offsets.

---

## 3. Vector Embeddings & Similarity Search

1. **Embedding Generation:**
   - 768-dimensional dense float vectors generated via `ModelRouter.embed(text)`.
   - In production, mapped to Google Gemini Embeddings (`text-embedding-004`) or OpenAI `text-embedding-3-small`.
   - In test/offline mode, generated using deterministic normalized unit vectors.
2. **Cosine Similarity Calculation:**
   $$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2} = \frac{\sum_{i=1}^n u_i v_i}{\sqrt{\sum_{i=1}^n u_i^2} \sqrt{\sum_{i=1}^n v_i^2}}$$
3. **Search Execution:**
   Embeds the user search query, evaluates cosine similarity across indexed chunks, filters by `min_similarity`, and returns top-$k$ ranked snippets.

---

## 4. Prompt Deduplication Engine

PromptForge AI features two-tier prompt deduplication:
1. **Exact Deduplication (Hash Fingerprint):**
   - Normalizes text (lowercase, punctuation stripping, whitespace collapsing).
   - Generates SHA-256 cryptographic digest.
   - O(1) detection of duplicate prompts.
2. **Semantic Deduplication (Vector Cosine Distance):**
   - Generates vector embedding of candidate prompt.
   - Computes cosine similarity against existing prompts in library.
   - Identifies conceptual duplicates if similarity exceeds threshold (default $0.88$).
