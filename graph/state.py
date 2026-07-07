from typing import Any, List, Optional, TypedDict


class SupportState(TypedDict, total=False):
    request_id: str
    user_message: str

    category: str
    priority: str
    requires_ticket: bool
    needs_more_info: bool
    clarifying_question: Optional[str]
    resolution_decision: str

    knowledge_results: List[str]
    knowledge_sources: List[dict[str, Any]]
    possible_solution: str
    retrieval_mode: str

    ticket_id: Optional[str]
    ticket_status: Optional[str]

    draft_response: str
    final_response: str

    validation_status: bool
    validation_feedback: Optional[str]
    validation_retry_count: int
    max_validation_retries: int

    error_message: Optional[str]
    interaction_logged: bool
