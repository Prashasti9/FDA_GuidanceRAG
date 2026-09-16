import json
import pathlib
from openai import OpenAI
from dotenv import load_dotenv
import chromadb

load_dotenv()

CHUNKS_FILE = pathlib.Path("data/chunks.jsonl")
CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "fda_guidance"
EMBED_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100

client = OpenAI()
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)


def load_chunks():
    with open(CHUNKS_FILE) as f:
        return [json.loads(line) for line in f]


def embed_batch(texts):
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]


def main():
    chunks = load_chunks()
    print(f"Embedding {len(chunks)} chunks in batches of {BATCH_SIZE}...")

    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        ids = [c["id"] for c in batch]
        metadatas = [
            {"source": c["source"], "page": c["page"], "section": c["section"], "url": c["url"]}
            for c in batch
        ]

        embeddings = embed_batch(texts)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"  Embedded {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks")

    print(f"\nDone. {collection.count()} chunks stored in Chroma at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
