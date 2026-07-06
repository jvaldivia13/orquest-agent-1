from graph.state import SupportState


def resolver_node(state: SupportState) -> SupportState:
    possible_solution = state.get("possible_solution", "")
    priority = state.get("priority", "Media")
    user_message = state.get("user_message", "").lower()

    requires_ticket = False
    if not possible_solution:
        requires_ticket = True
    if priority.lower() == "alta":
        requires_ticket = True
    if "bloqueada" in user_message or "mfa" in user_message:
        requires_ticket = True

    state["requires_ticket"] = requires_ticket
    return state
