from dataclasses import dataclass
from typing import Protocol, Literal


@dataclass(frozen=True)
class Chunk:
    id: str          # f"{source}::p{page}::c{idx}"
    text: str
    source: str      # e.g. "ICH-Q7-Good-Manufacturing-Practice.pdf"
    page: int
    section: str     # nearest heading above the chunk
    url: str         # FDA landing page, for clickable citations


@dataclass
class Answer:
    text: str
    citations: list[int]        # indices into `contexts`
    contexts: list[Chunk]
    abstained: bool
    prompt_version: str
    retrieval_config: Literal["vector", "hybrid", "hybrid_rerank"]
    latency_ms: dict[str, float]   # {"retrieve":..., "rerank":..., "generate":...}
    usage: dict[str, int]          # token counts


class Retriever(Protocol):
    def retrieve(self, query: str, k: int = 5) -> list[Chunk]:
        ...
