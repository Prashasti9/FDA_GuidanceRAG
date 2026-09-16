# FDA_GuidanceRAG — Progress

## Done
- Day 0: environment, API keys, repo, branch protection
- contracts.py: shared Chunk/Answer/Retriever definitions
- Corpus: 84 FDA CMC guidance PDFs downloaded, validated (all have real text layers)
- Parsing: ingest/parse.py — extracts text, page numbers, section headings → data/parsed.jsonl (1571 pages)
- Chunking: ingest/chunk.py — 600-token chunks, 100-token overlap → data/chunks.jsonl (2196 chunks)
- Embedding: ingest/embed.py — embedded all chunks into Chroma (data/chroma/)
- Retrieval: src/vector_retriever.py — real VectorRetriever implementing the Retriever protocol, tested and working

## Known limitation (found during testing)
- Corpus does not include ICH Q7 itself (only mentions/citations of it in other docs, 41 mentions).
  Pure vector search misses exact-term matches like "ICH Q7" in favor of semantically similar content.
  This is expected — motivates the hybrid (BM25 + vector) retrieval step later.

## Next up
- Person B track: prompt template with [n] citations + refusal, LangGraph pipeline
  (retrieve → generate → validate → retry/abstain), citation validator, Streamlit UI
- Then: BM25 + hybrid ensemble retrieval, cross-encoder reranking
- Then: golden evaluation set (80 questions)
