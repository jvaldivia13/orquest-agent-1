from graph.state import SupportState


def resolver_node(state: SupportState) -> SupportState:
    category = state.get("category", "Otro")
    possible_solution = state.get("possible_solution", "")
    priority = state.get("priority", "Media")
    user_message = state.get("user_message", "").lower()

    state["needs_more_info"] = False
    state["requires_ticket"] = False
    state["clarifying_question"] = None

    if category == "Otro" and not possible_solution:
        state["needs_more_info"] = True
        state["resolution_decision"] = "Solicitar más información por solicitud ambigua."
        state["clarifying_question"] = (
            "¿Puedes indicar qué servicio, aplicación, dispositivo o acceso presenta el problema?"
        )
        return state

    if not possible_solution:
        state["requires_ticket"] = True
        state["resolution_decision"] = "Crear ticket simulado por ausencia de solución conocida."
        return state

    if priority.lower() == "alta":
        state["requires_ticket"] = True
        state["resolution_decision"] = "Crear ticket simulado por prioridad alta."
        return state

    if any(term in user_message for term in ("bloqueada", "bloqueo", "mfa", "seguridad")):
        state["requires_ticket"] = True
        state["resolution_decision"] = "Crear ticket simulado por posible caso de seguridad o credenciales."
        return state

    state["resolution_decision"] = "Responder automáticamente con solución conocida."
    return state
