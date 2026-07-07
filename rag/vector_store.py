from pathlib import Path
from typing import Any


VECTOR_STORE_PATH = Path("data/vector_store")
COLLECTION_NAME = "support_knowledge"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _load_optional_dependencies() -> tuple[Any, Any]:
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError("RAG vector dependencies are not installed") from exc

    return chromadb, SentenceTransformer


def build_vector_index(
    documents: list[dict[str, Any]],
    persist_path: Path = VECTOR_STORE_PATH,
    collection_name: str = COLLECTION_NAME,
    embedding_model: str = EMBEDDING_MODEL,
) -> int:
    if not documents:
        return 0

    chromadb, SentenceTransformer = _load_optional_dependencies()
    model = SentenceTransformer(embedding_model)
    client = chromadb.PersistentClient(path=str(persist_path))
    collection = client.get_or_create_collection(name=collection_name)

    ids = [document["id"] for document in documents]
    texts = [document["text"] for document in documents]
    metadatas = [document["metadata"] for document in documents]
    embeddings = model.encode(texts).tolist()

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return len(documents)


def query_vector_index(
    category: str,
    user_message: str,
    top_k: int = 3,
    persist_path: Path = VECTOR_STORE_PATH,
    collection_name: str = COLLECTION_NAME,
    embedding_model: str = EMBEDDING_MODEL,
) -> list[dict[str, Any]]:
    try:
        chromadb, SentenceTransformer = _load_optional_dependencies()
        model = SentenceTransformer(embedding_model)
        client = chromadb.PersistentClient(path=str(persist_path))
        collection = client.get_collection(name=collection_name)
        query_embedding = model.encode([user_message])[0].tolist()
        where = {"category": category} if category else None
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        return []

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    matches: list[dict[str, Any]] = []
    for text, metadata, distance in zip(documents, metadatas, distances):
        score = 1 / (1 + float(distance))
        matches.append(
            {
                "id": str(metadata.get("id", "")),
                "category": str(metadata.get("category", "")),
                "title": str(metadata.get("title", "")),
                "content": str(text),
                "score": score,
            }
        )
    return matches
