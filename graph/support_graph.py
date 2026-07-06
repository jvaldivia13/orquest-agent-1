from langgraph.graph import END, StateGraph

from agents.classifier_agent import classifier_node
from agents.knowledge_agent import knowledge_node
from agents.resolver_agent import resolver_node
from agents.response_agent import response_node
from agents.ticketing_agent import ticketing_node
from agents.validator_agent import validator_node
from graph.routing import route_after_resolver, route_after_validator
from graph.state import SupportState


workflow = StateGraph(SupportState)

workflow.add_node("classifier", classifier_node)
workflow.add_node("knowledge", knowledge_node)
workflow.add_node("resolver", resolver_node)
workflow.add_node("ticketing", ticketing_node)
workflow.add_node("response", response_node)
workflow.add_node("validator", validator_node)

workflow.set_entry_point("classifier")

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
        END: END,
        "response": "response",
    },
)

support_graph = workflow.compile()
