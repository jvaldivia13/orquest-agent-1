from graph.state import SupportState


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
