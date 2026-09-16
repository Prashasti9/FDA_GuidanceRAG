# FDA_GuidanceRAG — Progress

## Done — Day 0
- Environment: Python 3.11 venv, all packages installed, imports verified (noted LangChain v1 import path change for `EnsembleRetriever`)
- Repo: GitHub repo created, branch ruleset active on `main` (PR required to merge)
- API keys: OpenAI key in `.env`, billing set up with a $10 hard spend limit (Cohere key present, not yet used)
- Corpus: 84 FDA CMC guidance PDFs downloaded (CDER, Topic: Chemistry, Manufacturing, and Controls), validated — all have real, extractable text layers

## Done — Day 1, Hour 0
- `contracts.py`: shared `Chunk`, `Answer`, `Retriever` definitions

## Done — Day 1, Hours 1-4 (retrieval track)
- Parsing: `ingest/parse.py` → `data/parsed.jsonl` (1,571 pages, page numbers + section headings extracted)
- Chunking: `ingest/chunk.py` → `data/chunks.jsonl` (2,196 chunks, 600 tokens / 100-token overlap)
- Embedding: `ingest/embed.py` → all chunks embedded (`text-embedding-3-small`) and stored in ChromaDB (`data/chroma/`)
- Retrieval: `src/vector_retriever.py` — real `VectorRetriever` implementing the `Retriever` protocol, tested and working

## Done — Day 1, Hours 1-4 (generation track)
- Prompt: `prompts/answer_v1.yaml` — enforces per-sentence/bullet citations, explicit refusal phrase, includes a correct/incorrect citation example
- Pipeline: `src/pipeline.py` — LangGraph graph: retrieve → generate (`gpt-4o-mini`) → validate → retry (max 1) → abstain
- Citation validator: `src/citation_validator.py` — strict per-claim checking (sentences + bullets split separately), citation range validation
- UI: `app.py` — working Streamlit demo (question in, cited answer + expandable sources + timing/token metrics out)

**Sync 1 (end of Hour 4) is complete** — both tracks merged and working together end-to-end.

## Done — Documentation
- `README.md` — public-facing project overview, architecture diagram (Mermaid), status table, tech stack
- `docs/demo-script.md` — shot-by-shot script for a 2-minute demo video (not yet recorded)

## Known findings from testing
- **Corpus does not include ICH Q7 itself** (only 41 chunk-level mentions/citations of it within other guidances). Pure vector search misses exact-term matches like "ICH Q7" in favor of semantically similar content. Verified this is a genuine retrieval limitation, not a bug — confirmed the retriever works correctly on in-corpus topics (e.g., container closure systems). This is the primary motivator for hybrid (BM25 + vector) retrieval next.
- **Citation coverage gap (found and fixed):** initial prompt + loose validator allowed answers with only one citation at the end of a multi-sentence, multi-bullet response. Fixed with a stronger prompt (explicit example of correct vs. incorrect citation style) and a stricter validator that checks bullets and sentences separately.
- Some Table-of-Contents pages produce a section heading with dot-leader/page-number artifacts — cosmetic only, doesn't affect content pages or answer quality.

## Next up — Day 1, Hours 5-8
- BM25 keyword retriever over the same chunk set
- Hybrid ensemble retriever (BM25 + vector, weighted fusion)
- Cross-encoder reranking (local model, optional Cohere comparison)
- `RETRIEVAL_MODE` config flag (vector / hybrid / hybrid_rerank) — needed for the ablation table
- Golden evaluation set (80 questions: single-chunk, multi-chunk, keyword/section, unanswerable, ambiguous)

## Then — Day 2
- Eval runner + response cache
- Deterministic metrics (recall@5, MRR, citation validity, abstention recall/precision)
- Ragas LLM-judged metrics (faithfulness, answer relevancy, context precision)
- Full ablation run across all 3 retrieval configs
- Abstention threshold calibration
- GitHub Actions CI gate with hard/soft thresholds, demonstrated failing on a deliberately broken PR
- Failure analysis on worst-scoring questions
- Final README additions (ablation table, methodology, failure analysis, cost/latency) + recorded demo video
