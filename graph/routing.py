from langgraph.graph import END

from graph.state import SupportState


def route_after_resolver(state: SupportState) -> str:
    if state.get("requires_ticket"):
        return "ticketing"
    return "response"


def route_after_validator(state: SupportState) -> str:
    if state.get("validation_status"):
        return END
    return "response"
