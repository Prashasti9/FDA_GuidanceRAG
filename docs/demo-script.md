# Demo Video Script (~2 minutes)

Record with Loom or QuickTime screen recording. Keep it casual — narrate like you're showing a colleague, not reading a script verbatim.

## Shot list

**0:00–0:15 — Hook**
- Show the Streamlit app open, empty.
- Say: "This is FDA GuidanceRAG — it answers questions from FDA regulatory guidance documents, with citations, and it knows when to say 'I don't know.'"

**0:15–0:45 — A real, well-answered question**
- Type: "What documentation should be included in an annual report for CMC postapproval manufacturing changes?"
- Let it run, show the answer with citation markers.
- Click into one expandable source — show the actual PDF excerpt, page number, and the "Open source document" link. Click it to prove it's real.

**0:45–1:05 — Abstention**
- Type an off-topic question, e.g. "What is the recommended treatment for a broken arm?"
- Show it correctly refuses instead of making something up.
- Say: "It only answers from what's actually in the documents — otherwise it says so."

**1:05–1:30 — Under the hood (architecture)**
- Show the architecture diagram from the README (or draw it quickly).
- Say: "Under the hood: PDFs get parsed, chunked, embedded, and stored in a vector database. A question retrieves the most relevant chunks, an LLM generates a cited answer, and a validator checks every citation before it's shown — if it fails, it retries once, then abstains rather than showing something ungrounded."

**1:30–1:50 — What's next**
- Mention the known limitation (vector search missing exact-term matches like "ICH Q7").
- Say: "That's exactly why the next phase adds hybrid search — combining keyword and meaning-based search — plus a formal evaluation suite with CI gating."

**1:50–2:00 — Close**
- Say: "Full write-up, architecture, and code are in the repo README."

## Tips
- Do 2-3 takes; keep the best.
- Trim dead air at the start/end.
- Upload the final Loom/video link at the top of the README once ready.
