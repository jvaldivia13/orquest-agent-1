VALIDATOR_PROMPT = (
    "Valida la respuesta final de soporte TI. Devuelve solo JSON con keys "
    "validation_status y validation_feedback. "
    "validation_status debe ser true si la respuesta es clara, coherente, segura, "
    "no solicita contrasenas y contiene el ticket cuando corresponde. "
    "Mensaje original: {user_message}. Categoria: {category}. "
    "Requiere ticket: {requires_ticket}. Ticket: {ticket_id}. "
    "Respuesta: {draft_response}"
)


def build_validator_prompt(state: dict) -> str:
    return VALIDATOR_PROMPT.format(
        user_message=state.get("user_message", ""),
        category=state.get("category", "Otro"),
        requires_ticket=state.get("requires_ticket", False),
        ticket_id=state.get("ticket_id") or "",
        draft_response=state.get("draft_response", ""),
    )
