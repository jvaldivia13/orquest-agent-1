from langgraph.graph import END

from graph.state import SupportState


def route_after_resolver(state: SupportState) -> str:
    if state.get("needs_more_info"):
        return "response"
    if state.get("requires_ticket"):
        return "ticketing"
    return "response"


def route_after_validator(state: SupportState) -> str:
    if state.get("validation_status"):
        return END
    if state.get("validation_retry_count", 0) >= state.get("max_validation_retries", 2):
        return END
    return "response"
