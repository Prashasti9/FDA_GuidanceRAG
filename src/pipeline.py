from typing import TypedDict
from langgraph.graph import StateGraph, END
from openai import OpenAI
from dotenv import load_dotenv
import time

from src.contracts import Answer, Chunk
from src.prompts import format_prompt
from src.vector_retriever import VectorRetriever

load_dotenv()
client = OpenAI()
retriever = VectorRetriever()

GENERATION_MODEL = "gpt-4o-mini"
PROMPT_VERSION = "v1"
MAX_RETRIES = 1


class RAGState(TypedDict):
    query: str
    contexts: list[Chunk]
    answer_text: str
    valid: bool
    abstained: bool
    attempts: int
    latency_ms: dict
    usage: dict


def retrieve_node(state: RAGState) -> RAGState:
    t0 = time.time()
    contexts = retriever.retrieve(state["query"], k=5)
    state["contexts"] = contexts
    state["latency_ms"] = {"retrieve": (time.time() - t0) * 1000}
    return state


def generate_node(state: RAGState) -> RAGState:
    t0 = time.time()
    prompt, _ = format_prompt(PROMPT_VERSION, state["query"], state["contexts"])

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    state["answer_text"] = response.choices[0].message.content
    state["latency_ms"]["generate"] = (time.time() - t0) * 1000
    state["usage"] = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
    }
    state["attempts"] = state.get("attempts", 0) + 1
    return state


def validate_node(state: RAGState) -> RAGState:
    answer = state["answer_text"]
    refusal_phrase = "I don't have enough information in the provided documents"

    if refusal_phrase in answer:
        state["valid"] = True
        state["abstained"] = True
        return state

    # Check every sentence-ending citation marker [n] is in valid range
    import re
    citations = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
    num_contexts = len(state["contexts"])

    if not citations:
        state["valid"] = False
    elif any(c < 1 or c > num_contexts for c in citations):
        state["valid"] = False
    else:
        state["valid"] = True

    state["abstained"] = False
    return state


def abstain_node(state: RAGState) -> RAGState:
    state["answer_text"] = "I don't have enough information in the provided documents to answer this question."
    state["abstained"] = True
    return state


def route_after_validate(state: RAGState) -> str:
    if state["valid"]:
        return "return"
    return "retry" if state["attempts"] < MAX_RETRIES + 1 else "abstain"


def build_graph():
    g = StateGraph(RAGState)
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)
    g.add_node("validate", validate_node)
    g.add_node("abstain", abstain_node)

    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", "validate")
    g.add_conditional_edges(
        "validate", route_after_validate,
        {"retry": "generate", "abstain": "abstain", "return": END}
    )
    g.add_edge("abstain", END)

    return g.compile()


def ask(query: str) -> Answer:
    graph = build_graph()
    result = graph.invoke({"query": query, "attempts": 0})

    return Answer(
        text=result["answer_text"],
        citations=[],
        contexts=result["contexts"],
        abstained=result["abstained"],
        prompt_version=PROMPT_VERSION,
        retrieval_config="vector",
        latency_ms=result["latency_ms"],
        usage=result["usage"],
    )


if __name__ == "__main__":
    test_questions = [
        "What documentation should be included in an annual report for CMC postapproval manufacturing changes?",
        "What is the recommended treatment for a broken arm?",  # should abstain
    ]

    for q in test_questions:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        answer = ask(q)
        print(f"\nA: {answer.text}")
        print(f"\nAbstained: {answer.abstained}")
        print(f"Latency: {answer.latency_ms}")
