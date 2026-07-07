from rag.retriever import EMPTY_RAG_RESULT, retrieve_relevant_context


def test_retrieve_relevant_context_returns_empty_when_vector_store_unavailable(monkeypatch):
    monkeypatch.setattr("rag.retriever.query_vector_index", lambda **_kwargs: [])

    result = retrieve_relevant_context(
        category="Red / conectividad",
        user_message="No puedo acceder a la intranet por VPN",
    )

    assert result == EMPTY_RAG_RESULT
