from llm.support_llm import classify_support_request
from graph.state import SupportState


def classifier_node(state: SupportState) -> SupportState:
    classification = classify_support_request(state.get("user_message", ""))

    state["category"] = classification["category"]
    state["priority"] = classification["priority"]
    state["requires_ticket"] = False
    state["needs_more_info"] = False
    return state
