from tools.knowledge_tools import search_knowledge_base


def test_search_knowledge_base_by_category():
    result = search_knowledge_base(
        category="Red / conectividad",
        user_message="No puedo conectarme a la VPN",
    )

    assert result["articles"]
    assert result["possible_solution"]


def test_search_knowledge_base_uses_rag_context_when_available(monkeypatch):
    monkeypatch.setattr(
        "tools.knowledge_tools.retrieve_relevant_context",
        lambda category, user_message: {
            "articles": [
                {
                    "id": "KB-RAG",
                    "category": category,
                    "title": "Resultado semantico",
                    "content": "Solucion recuperada por RAG.",
                    "score": 0.91,
                }
            ],
            "possible_solution": "Solucion recuperada por RAG.",
            "retrieval_mode": "vector",
        },
    )

    result = search_knowledge_base(
        category="Red / conectividad",
        user_message="No puedo acceder a recursos internos desde fuera de oficina",
    )

    assert result["articles"][0]["id"] == "KB-RAG"
    assert result["possible_solution"] == "Solucion recuperada por RAG."
    assert result["retrieval_mode"] == "vector"


def test_search_knowledge_base_prioritizes_keywords():
    result = search_knowledge_base(
        category="Acceso / autenticación",
        user_message="No funciona mi MFA al iniciar sesión",
    )

    assert result["articles"][0]["id"] == "KB-004"
    assert "MFA" in result["possible_solution"]


def test_search_knowledge_base_unknown_category_returns_empty_result():
    result = search_knowledge_base(
        category="Categoría inexistente",
        user_message="Algo falla",
    )

    assert result == {"articles": [], "possible_solution": ""}


def test_search_knowledge_base_finds_lost_mfa_device_case():
    result = search_knowledge_base(
        category="Acceso / autenticaci\u00f3n",
        user_message="Perdi mi celular y no puedo usar MFA para iniciar sesion",
    )

    assert result["articles"][0]["id"] == "KB-006"
    assert "restablecimiento de MFA" in result["possible_solution"]


def test_search_knowledge_base_finds_printer_case():
    result = search_knowledge_base(
        category="Hardware",
        user_message="No puedo imprimir en la impresora de la oficina",
    )

    assert result["articles"][0]["id"] == "KB-015"
    assert "cola de impresion" in result["possible_solution"]


def test_search_knowledge_base_finds_outlook_sync_case():
    result = search_knowledge_base(
        category="Software",
        user_message="Outlook no sincroniza mi correo desde ayer",
    )

    assert result["articles"][0]["id"] == "KB-020"
    assert "perfil de Outlook" in result["possible_solution"]


def test_search_knowledge_base_finds_access_request_case():
    result = search_knowledge_base(
        category="Solicitud administrativa",
        user_message="Solicito acceso al sistema financiero para cierre mensual",
    )

    assert result["articles"][0]["id"] == "KB-026"
    assert "aprobacion del responsable" in result["possible_solution"]
