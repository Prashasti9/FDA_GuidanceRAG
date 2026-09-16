import re

CITATION_PATTERN = re.compile(r"\[(\d+)\]")
REFUSAL_PHRASE = "I don't have enough information in the provided documents"


def split_sentences(text: str) -> list[str]:
    """Naive sentence splitter — splits on '. ', '? ', '! ' followed by a capital letter or end of string."""
    # Keep it simple and predictable rather than pulling in a full NLP sentence splitter
    parts = re.split(r'(?<=[.?!])\s+(?=[A-Z]|$)', text.strip())
    return [p.strip() for p in parts if p.strip()]


def is_list_item_or_heading(sentence: str) -> bool:
    """Skip validation for bullet points, headers, or very short fragments that aren't real factual claims."""
    stripped = sentence.strip()
    if stripped.startswith(("-", "*", "•")):
        return True
    if len(stripped) < 15:
        return True
    if stripped.endswith(":"):
        return True
    return False


def validate_citations(answer_text: str, num_contexts: int) -> dict:
    """
    Returns a dict with:
      - valid: bool
      - errors: list of human-readable problems found
    """
    errors = []

    if REFUSAL_PHRASE in answer_text:
        return {"valid": True, "errors": []}

    sentences = split_sentences(answer_text)
    factual_sentences = [s for s in sentences if not is_list_item_or_heading(s)]

    if not factual_sentences:
        errors.append("No factual sentences found to validate.")

    for sentence in factual_sentences:
        citations = CITATION_PATTERN.findall(sentence)
        if not citations:
            errors.append(f"Missing citation: \"{sentence[:80]}...\"")
            continue
        for c in citations:
            c_int = int(c)
            if c_int < 1 or c_int > num_contexts:
                errors.append(f"Out-of-range citation [{c_int}] (only {num_contexts} contexts provided) in: \"{sentence[:80]}...\"")

    all_citations = CITATION_PATTERN.findall(answer_text)
    if any(int(c) < 1 or int(c) > num_contexts for c in all_citations):
        pass  # already caught above per-sentence

    return {"valid": len(errors) == 0, "errors": errors}


if __name__ == "__main__":
    # Quick smoke tests
    good = "The applicant must submit a report. [1] The change must be documented within 30 days. [2]"
    bad_missing = "The applicant must submit a report. The change must be documented within 30 days. [2]"
    bad_range = "The applicant must submit a report. [7]"
    refusal = "I don't have enough information in the provided documents to answer this question."

    for label, text in [("good", good), ("bad_missing", bad_missing), ("bad_range", bad_range), ("refusal", refusal)]:
        result = validate_citations(text, num_contexts=5)
        print(f"{label}: valid={result['valid']}, errors={result['errors']}")
