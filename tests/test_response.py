from agents import response_agent
from agents.response_agent import response_node


def test_response_uses_llm_text_when_available(monkeypatch):
    monkeypatch.setattr(
        response_agent,
        "build_support_response",
        lambda _state: "Respuesta generada por DeepSeek.",
    )

    result = response_agent.response_node(
        {
            "category": "Red / conectividad",
            "possible_solution": "Reiniciar cliente VPN.",
            "requires_ticket": False,
        }
    )

    assert result["draft_response"] == "Respuesta generada por DeepSeek."


def test_response_asks_clarifying_question():
    result = response_node(
        {
            "category": "Otro",
            "needs_more_info": True,
            "clarifying_question": "¿Qué componente falla?",
        }
    )

    assert "necesitamos un poco más de información" in result["draft_response"]
    assert "¿Qué componente falla?" in result["draft_response"]


def test_response_does_not_claim_ticket_without_ticket_id():
    result = response_node(
        {
            "category": "Software",
            "requires_ticket": True,
            "possible_solution": "",
        }
    )

    assert "no se pudo generar el ticket" in result["draft_response"]
    assert "Se ha generado el ticket" not in result["draft_response"]
