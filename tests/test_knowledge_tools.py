from tools.knowledge_tools import search_knowledge_base


def test_search_knowledge_base_by_category():
    result = search_knowledge_base(
        category="Red / conectividad",
        user_message="No puedo conectarme a la VPN",
    )

    assert result["articles"]
    assert result["possible_solution"]


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
