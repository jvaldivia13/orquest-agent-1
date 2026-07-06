import json
from typing import Any

from app.config import settings
from llm.deepseek_client import get_deepseek_reasoner


ALLOWED_CATEGORIES = {
    "Acceso / autenticación",
    "Red / conectividad",
    "Hardware",
    "Software",
    "Solicitud administrativa",
    "Otro",
}

ALLOWED_PRIORITIES = {"Baja", "Media", "Alta"}


def _fallback_classification(user_message: str) -> dict[str, str]:
    message = user_message.lower()
    category = "Otro"

    if any(term in message for term in ("login", "contraseña", "mfa", "cuenta", "sesión")):
        category = "Acceso / autenticación"
    elif any(term in message for term in ("vpn", "wi-fi", "wifi", "conexión", "internet", "red")):
        category = "Red / conectividad"
    elif any(term in message for term in ("laptop", "monitor", "teclado", "mouse", "pantalla")):
        category = "Hardware"
    elif any(term in message for term in ("aplicación", "instalación", "software", "programa", "error")):
        category = "Software"
    elif any(term in message for term in ("permiso", "aprobación", "solicito acceso")):
        category = "Solicitud administrativa"

    priority = "Alta" if any(
        term in message for term in ("toda la oficina", "masivo", "crítico", "urgente")
    ) else "Media"
    return {"category": category, "priority": priority}


def classify_support_request(user_message: str) -> dict[str, str]:
    if not settings.DEEPSEEK_API_KEY:
        return _fallback_classification(user_message)

    prompt = (
        "Clasifica el requerimiento de soporte TI. "
        "Devuelve solo JSON con keys category y priority. "
        "Categorías permitidas: Acceso / autenticación, Red / conectividad, Hardware, "
        "Software, Solicitud administrativa, Otro. Prioridades: Baja, Media, Alta. "
        f"Mensaje: {user_message}"
    )

    try:
        response = get_deepseek_reasoner().invoke(prompt)
        content = getattr(response, "content", str(response))
        parsed: dict[str, Any] = json.loads(content)
        category = str(parsed.get("category", "Otro"))
        priority = str(parsed.get("priority", "Media")).capitalize()
    except Exception:
        return _fallback_classification(user_message)

    if category not in ALLOWED_CATEGORIES:
        category = "Otro"
    if priority not in ALLOWED_PRIORITIES:
        priority = "Media"

    return {"category": category, "priority": priority}
