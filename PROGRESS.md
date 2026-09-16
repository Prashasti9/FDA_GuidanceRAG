# FDA_GuidanceRAG — Progress

## Done — Day 0
- Environment: Python 3.11 venv, all packages installed, imports verified
- Repo: GitHub repo created, branch ruleset active (PR required to merge to main)
- API keys: OpenAI key in .env, billing set up with a $10 hard spend limit

## Done — Day 1, Hour 0
- contracts.py: shared Chunk, Answer, Retriever definitions

## Done — Day 1, Hours 1-4 (retrieval track)
- Corpus: 84 FDA CMC guidance PDFs downloaded, validated (all have real text layers)
- Parsing: ingest/parse.py → data/parsed.jsonl (1571 pages, page numbers + section headings)
- Chunking: ingest/chunk.py → data/chunks.jsonl (2196 chunks, 600 tokens/100 overlap)
- Embedding: ingest/embed.py → all chunks embedded into Chroma (data/chroma/)
- Retrieval: src/vector_retriever.py — real VectorRetriever, tested and working

## Done — Day 1, Hours 1-4 (generation track)
- Prompt: prompts/answer_v1.yaml — enforces per-sentence/bullet citations, explicit refusal
- Pipeline: src/pipeline.py — LangGraph graph: retrieve → generate → validate → retry/abstain
- Citation validator: src/citation_validator.py — strict per-claim checking (sentences + bullets), range validation
- UI: app.py — working Streamlit demo (question in, cited answer + expandable sources + timing/token metrics out)

Sync 1 (end of Hour 4) is complete — both tracks merged and working together end-to-end.

## Known limitation (found during testing)
- Corpus does not include ICH Q7 itself (only 41 mentions/citations of it within other docs).
  Pure vector search misses exact-term matches like "ICH Q7" in favor of semantically similar
  content. Expected — motivates the hybrid (BM25 + vector) retrieval step next.
- Some page sections still show "Unknown Section" — heading-detection regex doesn't catch every
  FDA formatting style. Doesn't affect answer quality, just cosmetic in the sources list.

## Next up — Day 1, Hours 5-8
- BM25 keyword retriever
- Hybrid ensemble retriever (BM25 + vector, weighted)
- Cross-encoder reranking
- RETRIEVAL_MODE config flag (vector / hybrid / hybrid_rerank) — needed for the ablation table
- Golden evaluation set (80 questions: single-chunk, multi-chunk, keyword/section, unanswerable, ambiguous)

## Then — Day 2
- Eval runner + deterministic metrics (recall@5, MRR, citation validity, abstention recall/precision)
- Ragas LLM-judged metrics (faithfulness, answer relevancy, context precision)
- Full ablation run across all 3 retrieval configs
- GitHub Actions CI gate with hard/soft thresholds
- Failure analysis + README + demo video
