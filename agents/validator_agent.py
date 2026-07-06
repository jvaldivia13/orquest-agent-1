from graph.state import SupportState


def validator_node(state: SupportState) -> SupportState:
    draft_response = state.get("draft_response", "")
    requires_ticket = state.get("requires_ticket", False)
    ticket_id = state.get("ticket_id")

    if not draft_response:
        state["validation_status"] = False
        state["validation_feedback"] = "La respuesta está vacía."
        return state

    if requires_ticket and ticket_id and ticket_id not in draft_response:
        state["validation_status"] = False
        state["validation_feedback"] = "La respuesta no incluye el ticket generado."
        return state

    state["validation_status"] = True
    state["final_response"] = draft_response
    return state
