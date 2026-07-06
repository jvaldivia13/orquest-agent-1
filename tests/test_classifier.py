import pytest

from agents.classifier_agent import classifier_node
from app.config import settings


@pytest.fixture(autouse=True)
def force_local_fallback(monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "")


def test_classifier_access_request():
    result = classifier_node({"user_message": "No puedo acceder a mi cuenta"})

    assert result["category"] == "Acceso / autenticación"
    assert result["priority"] == "Media"


def test_classifier_vpn_request():
    result = classifier_node({"user_message": "No puedo conectarme a la VPN"})

    assert result["category"] == "Red / conectividad"


def test_classifier_high_priority_for_massive_impact():
    result = classifier_node(
        {"user_message": "Toda la oficina está sin internet y no podemos trabajar"}
    )

    assert result["category"] == "Red / conectividad"
    assert result["priority"] == "Alta"


def test_classifier_unknown_request_goes_to_other():
    result = classifier_node({"user_message": "Tengo un problema extraño"})

    assert result["category"] == "Otro"
