import re

CITATION_PATTERN = re.compile(r"\[(\d+)\]")
REFUSAL_PHRASE = "I don't have enough information in the provided documents"


def split_into_claims(text: str) -> list[str]:
    """
    Split text into individual claims to validate: both sentences and bullet lines.
    Bullets are split on newlines first, then each non-bullet block is sentence-split.
    """
    claims = []
    lines = text.split("\n")

    buffer = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("-", "*", "•")):
            # Flush any buffered prose first
            if buffer:
                claims.extend(_sentence_split(" ".join(buffer)))
                buffer = []
            claims.append(stripped)
        else:
            buffer.append(stripped)
    if buffer:
        claims.extend(_sentence_split(" ".join(buffer)))

    return claims


def _sentence_split(text: str) -> list[str]:
    parts = re.split(r'(?<=[.?!])\s+(?=[A-Z]|$)', text.strip())
    return [p.strip() for p in parts if p.strip()]


def is_headingish(claim: str) -> bool:
    """Skip validation for very short fragments or lines that are just headers."""
    stripped = claim.strip()
    if len(stripped) < 15:
        return True
    if stripped.endswith(":"):
        return True
    return False


def validate_citations(answer_text: str, num_contexts: int) -> dict:
    errors = []

    if REFUSAL_PHRASE in answer_text:
        return {"valid": True, "errors": []}

    claims = split_into_claims(answer_text)
    factual_claims = [c for c in claims if not is_headingish(c)]

    if not factual_claims:
        errors.append("No factual claims found to validate.")

    for claim in factual_claims:
        citations = CITATION_PATTERN.findall(claim)
        if not citations:
            errors.append(f"Missing citation: \"{claim[:80]}\"")
            continue
        for c in citations:
            c_int = int(c)
            if c_int < 1 or c_int > num_contexts:
                errors.append(f"Out-of-range citation [{c_int}] (only {num_contexts} contexts provided) in: \"{claim[:80]}\"")

    return {"valid": len(errors) == 0, "errors": errors}


if __name__ == "__main__":
    good = "The applicant must submit a report. [1]\n- A summary of the change. [1]\n- Supporting test data. [2]"
    bad_missing_intro = "The applicant must submit a report.\n- A summary of the change. [1]\n- Supporting test data. [2]"
    bad_missing_bullet = "The applicant must submit a report. [1]\n- A summary of the change.\n- Supporting test data. [2]"
    refusal = "I don't have enough information in the provided documents to answer this question."

    for label, text in [("good", good), ("bad_missing_intro", bad_missing_intro), ("bad_missing_bullet", bad_missing_bullet), ("refusal", refusal)]:
        result = validate_citations(text, num_contexts=5)
        print(f"{label}: valid={result['valid']}, errors={result['errors']}")
