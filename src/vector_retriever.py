import chromadb
from openai import OpenAI
from dotenv import load_dotenv

from src.contracts import Chunk

load_dotenv()

CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "fda_guidance"
EMBED_MODEL = "text-embedding-3-small"


class VectorRetriever:
    def __init__(self):
        self.client = OpenAI()
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)

    def _embed_query(self, query: str):
        response = self.client.embeddings.create(model=EMBED_MODEL, input=[query])
        return response.data[0].embedding

    def retrieve(self, query: str, k: int = 5) -> list[Chunk]:
        query_embedding = self._embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        chunks = []
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]
            chunks.append(Chunk(
                id=results["ids"][0][i],
                text=results["documents"][0][i],
                source=metadata["source"],
                page=metadata["page"],
                section=metadata["section"],
                url=metadata["url"],
            ))
        return chunks


if __name__ == "__main__":
    retriever = VectorRetriever()
    test_query = "What documentation does ICH Q7 require for equipment cleaning?"
    results = retriever.retrieve(test_query, k=3)

    print(f"Query: {test_query}\n")
    for i, chunk in enumerate(results, 1):
        print(f"--- Result {i} ---")
        print(f"Source: {chunk.source}, Page: {chunk.page}")
        print(f"Section: {chunk.section}")
        print(f"Text preview: {chunk.text[:200]}...")
        print()
