from graph.state import SupportState
from llm.support_llm import validate_support_response


def _fail(state: SupportState, feedback: str) -> SupportState:
    retry_count = state.get("validation_retry_count", 0) + 1
    max_retries = state.get("max_validation_retries", 2)
    state["validation_retry_count"] = retry_count
    state["validation_feedback"] = feedback

    if retry_count >= max_retries:
        state["validation_status"] = True
        state["final_response"] = (
            "No pudimos construir una respuesta validada automáticamente. "
            "Por favor, intenta describir el problema con más detalle."
        )
    else:
        state["validation_status"] = False
    return state


def validator_node(state: SupportState) -> SupportState:
    state.setdefault("validation_retry_count", 0)
    state.setdefault("max_validation_retries", 2)

    llm_validation = validate_support_response(state)
    if llm_validation:
        state["validation_status"] = bool(llm_validation.get("validation_status", False))
        state["validation_feedback"] = llm_validation.get("validation_feedback")
        if state["validation_status"]:
            state["final_response"] = state.get("draft_response", "")
        return state

    draft_response = state.get("draft_response", "")
    requires_ticket = state.get("requires_ticket", False)
    ticket_id = state.get("ticket_id")

    if not draft_response:
        return _fail(state, "La respuesta está vacía.")

    if "contraseña" in draft_response.lower() and "comparte" in draft_response.lower():
        return _fail(state, "La respuesta podría solicitar datos sensibles.")

    if requires_ticket and not ticket_id:
        return _fail(state, "La respuesta requiere ticket, pero no existe ticket generado.")

    if requires_ticket and ticket_id not in draft_response:
        return _fail(state, "La respuesta no incluye el ticket generado.")

    state["validation_status"] = True
    state["final_response"] = draft_response
    return state
