from graph.state import SupportState


def classifier_node(state: SupportState) -> SupportState:
    user_message = state.get("user_message", "").lower()

    category = "Otro"
    if any(term in user_message for term in ("login", "contraseña", "mfa", "cuenta")):
        category = "Acceso / autenticación"
    elif any(term in user_message for term in ("vpn", "wi-fi", "wifi", "conexión", "internet")):
        category = "Red / conectividad"
    elif any(term in user_message for term in ("laptop", "monitor", "teclado", "mouse")):
        category = "Hardware"
    elif any(term in user_message for term in ("aplicación", "instalación", "software", "programa")):
        category = "Software"
    elif any(term in user_message for term in ("permiso", "acceso", "aprobación")):
        category = "Solicitud administrativa"

    state["category"] = category
    state["priority"] = "Media"
    state["requires_ticket"] = False
    return state
