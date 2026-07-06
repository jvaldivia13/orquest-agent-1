from datetime import datetime

from langgraph.graph import END, StateGraph

from agents.classifier_agent import classifier_node
from agents.knowledge_agent import knowledge_node
from agents.resolver_agent import resolver_node
from agents.response_agent import response_node
from agents.ticketing_agent import ticketing_node
from agents.validator_agent import validator_node
from graph.routing import route_after_resolver, route_after_validator
from graph.state import SupportState
from tools.logging_tools import append_interaction_log


def initialize_request_node(state: SupportState) -> SupportState:
    if not state.get("request_id"):
        state["request_id"] = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    return state


def log_interaction_node(state: SupportState) -> SupportState:
    append_interaction_log(state)
    state["interaction_logged"] = True
    return state


workflow = StateGraph(SupportState)

workflow.add_node("initialize_request", initialize_request_node)
workflow.add_node("classifier", classifier_node)
workflow.add_node("knowledge", knowledge_node)
workflow.add_node("resolver", resolver_node)
workflow.add_node("ticketing", ticketing_node)
workflow.add_node("response", response_node)
workflow.add_node("validator", validator_node)
workflow.add_node("log_interaction", log_interaction_node)

workflow.set_entry_point("initialize_request")

workflow.add_edge("initialize_request", "classifier")
workflow.add_edge("classifier", "knowledge")
workflow.add_edge("knowledge", "resolver")
workflow.add_conditional_edges(
    "resolver",
    route_after_resolver,
    {
        "ticketing": "ticketing",
        "response": "response",
    },
)
workflow.add_edge("ticketing", "response")
workflow.add_edge("response", "validator")
workflow.add_conditional_edges(
    "validator",
    route_after_validator,
    {
        "response": "response",
        "log_interaction": "log_interaction",
    },
)
workflow.add_edge("log_interaction", END)

support_graph = workflow.compile()
