import json
import logging
from typing import Any

from app.config import settings
from llm.deepseek_client import get_deepseek_reasoner
from prompts.classifier_prompt import build_classifier_prompt


logger = logging.getLogger(__name__)


ALLOWED_CATEGORIES = {
    "Acceso / autenticaci\u00f3n",
    "Red / conectividad",
    "Hardware",
    "Software",
    "Solicitud administrativa",
    "Otro",
}

ALLOWED_PRIORITIES = {"Baja", "Media", "Alta"}


def parse_llm_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("LLM response does not contain a JSON object")

    parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON is not an object")
    return parsed


def _fallback_classification(user_message: str) -> dict[str, str]:
    message = user_message.lower()
    category = "Otro"

    if any(
        term in message
        for term in ("login", "contrase\u00f1a", "mfa", "cuenta", "sesi\u00f3n")
    ):
        category = "Acceso / autenticaci\u00f3n"
    elif any(
        term in message for term in ("vpn", "wi-fi", "wifi", "conexi\u00f3n", "internet", "red")
    ):
        category = "Red / conectividad"
    elif any(
        term in message
        for term in (
            "laptop",
            "monitor",
            "teclado",
            "mouse",
            "pantalla",
            "impresora",
            "imprimir",
        )
    ):
        category = "Hardware"
    elif any(
        term in message
        for term in (
            "aplicaci\u00f3n",
            "instalaci\u00f3n",
            "software",
            "programa",
            "error",
            "outlook",
            "correo",
            "teams",
            "office",
        )
    ):
        category = "Software"
    elif any(
        term in message for term in ("permiso", "aprobaci\u00f3n", "solicito acceso")
    ):
        category = "Solicitud administrativa"

    priority = (
        "Alta"
        if any(term in message for term in ("toda la oficina", "masivo", "cr\u00edtico", "urgente"))
        else "Media"
    )
    return {"category": category, "priority": priority}


def classify_support_request(user_message: str) -> dict[str, str]:
    if not settings.DEEPSEEK_API_KEY:
        return _fallback_classification(user_message)

    try:
        prompt = build_classifier_prompt(user_message)
        response = get_deepseek_reasoner().invoke(prompt)
        content = getattr(response, "content", str(response))
        parsed = parse_llm_json_object(content)
        category = str(parsed.get("category", "Otro"))
        priority = str(parsed.get("priority", "Media")).capitalize()
    except Exception:
        logger.warning("Falling back to local classification after invalid LLM response")
        return _fallback_classification(user_message)

    if category not in ALLOWED_CATEGORIES:
        category = "Otro"
    if priority not in ALLOWED_PRIORITIES:
        priority = "Media"

    return {"category": category, "priority": priority}
