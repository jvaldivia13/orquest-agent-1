from graph.state import SupportState
from tools.ticketing_tools import create_support_ticket


def ticketing_node(state: SupportState) -> SupportState:
    result = create_support_ticket(
        category=state.get("category", "Otro"),
        description=state.get("user_message", ""),
        priority=state.get("priority", "Media"),
    )

    state["ticket_id"] = result.get("ticket_id")
    state["ticket_status"] = result.get("status")
    return state
