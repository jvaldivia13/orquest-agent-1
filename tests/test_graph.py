from graph.support_graph import support_graph


def test_graph_returns_final_response():
    result = support_graph.invoke({"user_message": "No puedo conectarme a la VPN"})

    assert result["final_response"]
    assert result["category"] == "Red / conectividad"
