from graph.state import SupportState
from llm.support_llm import build_support_response


def response_node(state: SupportState) -> SupportState:
    llm_response = build_support_response(state)
    if llm_response:
        state["draft_response"] = llm_response
        return state

    if state.get("needs_more_info"):
        question = state.get("clarifying_question") or "¿Puedes compartir más detalle del problema?"
        state["draft_response"] = (
            "Para ayudarte correctamente, necesitamos un poco más de información.\n\n"
            f"{question}"
        )
        return state

    category = state.get("category", "Otro")
    possible_solution = state.get("possible_solution", "")
    requires_ticket = state.get("requires_ticket", False)
    ticket_id = state.get("ticket_id")

    response = f"Hemos identificado que tu solicitud está relacionada con {category}.\n\n"

    if possible_solution:
        response += f"Recomendación inicial: {possible_solution}\n\n"

    if requires_ticket and ticket_id:
        response += f"Se ha generado el ticket simulado {ticket_id} para seguimiento."
    elif requires_ticket:
        response += "El caso requiere soporte, pero no se pudo generar el ticket simulado."
    else:
        response += "Puedes seguir los pasos indicados. Si el problema continúa, contacta al equipo de soporte."

    state["draft_response"] = response
    return state
