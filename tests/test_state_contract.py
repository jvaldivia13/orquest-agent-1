from graph.state import SupportState


EXPECTED_FIELDS = {
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
    assert EXPECTED_FIELDS.issubset(SupportState.__annotations__)


def test_support_state_is_optional_total_false_contract():
    assert SupportState.__total__ is False
