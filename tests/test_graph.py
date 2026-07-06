import pytest

from app.config import settings
from graph.support_graph import support_graph


@pytest.fixture(autouse=True)
def force_local_fallback(monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "")


def test_graph_returns_final_response_for_known_solution():
    result = support_graph.invoke({"user_message": "No puedo conectarme a la VPN"})

    assert result["final_response"]
    assert result["category"] == "Red / conectividad"
    assert result["requires_ticket"] is False


def test_graph_creates_ticket_for_mfa_issue():
    result = support_graph.invoke({"user_message": "No funciona mi MFA"})

    assert result["category"] == "Acceso / autenticación"
    assert result["requires_ticket"] is True
    assert result["ticket_id"].startswith("INC-")
    assert result["ticket_id"] in result["final_response"]


def test_graph_asks_more_info_for_ambiguous_request():
    result = support_graph.invoke({"user_message": "Tengo un problema con mi equipo"})

    assert result["needs_more_info"] is True
    assert "más de información" in result["final_response"]
