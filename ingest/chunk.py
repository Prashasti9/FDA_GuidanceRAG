import json
import pathlib
import re
import tiktoken

INPUT_FILE = pathlib.Path("data/parsed.jsonl")
OUTPUT_FILE = pathlib.Path("data/chunks.jsonl")

CHUNK_SIZE = 600     # tokens
CHUNK_OVERLAP = 100  # tokens

encoding = tiktoken.get_encoding("cl100k_base")


def split_into_token_chunks(text, chunk_size, overlap):
    """Split text into overlapping chunks based on token count."""
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        if end >= len(tokens):
            break
        start = end - overlap
    return chunks


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    all_chunks = []
    chunk_counter_per_source = {}

    with open(INPUT_FILE) as f:
        pages = [json.loads(line) for line in f]

    print(f"Chunking {len(pages)} page-records...")

    for page in pages:
        source = page["source"]
        text_chunks = split_into_token_chunks(page["text"], CHUNK_SIZE, CHUNK_OVERLAP)

        for chunk_text in text_chunks:
            idx = chunk_counter_per_source.get(source, 0)
            chunk_id = f"{source}::p{page['page']}::c{idx}"
            chunk_counter_per_source[source] = idx + 1

            all_chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "source": source,
                "page": page["page"],
                "section": page["section"],
                "url": f"https://www.fda.gov/media/{source.replace('fda_', '').replace('.pdf', '')}/download",
            })

    with open(OUTPUT_FILE, "w") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"\nDone. {len(all_chunks)} chunks written to {OUTPUT_FILE}")
    print(f"Average chunks per page: {len(all_chunks) / len(pages):.2f}")


if __name__ == "__main__":
    main()
