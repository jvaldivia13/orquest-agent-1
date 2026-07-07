from typing import Any

from rag.vector_store import query_vector_index


EMPTY_RAG_RESULT = {"articles": [], "possible_solution": "", "retrieval_mode": "none"}


def retrieve_relevant_context(
    category: str,
    user_message: str,
    top_k: int = 3,
) -> dict[str, Any]:
    matches = query_vector_index(
        category=category,
        user_message=user_message,
        top_k=top_k,
    )

    if not matches:
        return EMPTY_RAG_RESULT

    return {
        "articles": matches,
        "possible_solution": str(matches[0].get("content", "")),
        "retrieval_mode": "vector",
    }
