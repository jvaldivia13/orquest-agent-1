from tools.knowledge_tools import search_knowledge_base


def test_search_knowledge_base_by_category():
    result = search_knowledge_base(
        category="Red / conectividad",
        user_message="No puedo conectarme a la VPN",
    )

    assert result["articles"]
    assert result["possible_solution"]
