import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.api import app
from app.config import settings


client = TestClient(app)


@pytest.fixture(autouse=True)
def force_local_fallback(monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "")


def test_support_request_rejects_empty_message():
    response = client.post("/support/request", json={"message": ""})

    assert response.status_code == 422


def test_support_request_returns_response():
    response = client.post(
        "/support/request",
        json={"message": "No puedo conectarme a la VPN"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Red / conectividad"
    assert body["response"]


def test_root_serves_frontend():
    response = client.get("/")

    assert response.status_code == 200
    assert "Agentic Support Orchestrator" in response.text
    assert "/support/request" in response.text


def test_cli_rejects_empty_message(monkeypatch, capsys):
    def fail_if_invoked(_state):
        raise AssertionError("support graph should not be invoked")

    monkeypatch.setattr("builtins.input", lambda _prompt: "   ")
    monkeypatch.setattr(main_module.support_graph, "invoke", fail_if_invoked)

    main_module.main()

    assert "Debes ingresar un requerimiento para continuar." in capsys.readouterr().out


def test_cli_rejects_message_over_2000_characters(monkeypatch, capsys):
    def fail_if_invoked(_state):
        raise AssertionError("support graph should not be invoked")

    monkeypatch.setattr("builtins.input", lambda _prompt: "x" * 2001)
    monkeypatch.setattr(main_module.support_graph, "invoke", fail_if_invoked)

    main_module.main()

    assert (
        "El requerimiento supera el máximo permitido de 2000 caracteres."
        in capsys.readouterr().out
    )
