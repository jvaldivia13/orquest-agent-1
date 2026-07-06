from graph.state import SupportState


EXPECTED_SUPPORT_STATE_FIELDS = {
    "request_id",
    "user_message",
    "category",
    "priority",
    "requires_ticket",
    "needs_more_info",
    "clarifying_question",
    "resolution_decision",
    "knowledge_results",
    "possible_solution",
    "ticket_id",
    "ticket_status",
    "draft_response",
    "final_response",
    "validation_status",
    "validation_feedback",
    "validation_retry_count",
    "max_validation_retries",
    "error_message",
    "interaction_logged",
}


def test_support_state_declares_required_flow_fields():
    assert EXPECTED_SUPPORT_STATE_FIELDS.issubset(SupportState.__annotations__)


def test_support_state_accepts_required_flow_fields():
    state: SupportState = {
        "request_id": "REQ-1",
        "user_message": "Tengo un problema",
        "category": "Otro",
        "priority": "Media",
        "requires_ticket": False,
        "needs_more_info": True,
        "clarifying_question": "¿Puedes indicar qué componente falla?",
        "validation_retry_count": 0,
        "max_validation_retries": 2,
        "resolution_decision": "Solicitar más información.",
    }

    assert state["needs_more_info"] is True
    assert state["max_validation_retries"] == 2
