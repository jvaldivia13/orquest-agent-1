from graph.state import SupportState
from tools.knowledge_tools import search_knowledge_base


def knowledge_node(state: SupportState) -> SupportState:
    result = search_knowledge_base(
        category=state.get("category", ""),
        user_message=state.get("user_message", ""),
    )

    state["knowledge_results"] = [
        f"{article['id']}: {article['title']}"
        for article in result.get("articles", [])
    ]
    state["possible_solution"] = result.get("possible_solution", "")
    return state
