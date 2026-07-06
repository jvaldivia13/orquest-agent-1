from typing import List, Optional, TypedDict


class SupportState(TypedDict, total=False):
    request_id: str
    user_message: str

    category: str
    priority: str
    requires_ticket: bool

    knowledge_results: List[str]
    possible_solution: str

    ticket_id: Optional[str]
    ticket_status: Optional[str]

    draft_response: str
    final_response: str

    validation_status: bool
    validation_feedback: Optional[str]

    error_message: Optional[str]
