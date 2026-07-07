RESPONSE_PROMPT = (
    "Construye una respuesta clara, profesional y accionable para el usuario final de soporte TI. "
    "No solicites contrasenas ni datos sensibles. "
    "Categoria: {category}. Prioridad: {priority}. "
    "Mensaje original: {user_message}. "
    "Solucion conocida: {possible_solution}. "
    "Requiere ticket: {requires_ticket}. Ticket: {ticket_id}. "
    "Pregunta aclaratoria: {clarifying_question}."
)


def build_response_prompt(state: dict) -> str:
    return RESPONSE_PROMPT.format(
        category=state.get("category", "Otro"),
        priority=state.get("priority", "Media"),
        user_message=state.get("user_message", ""),
        possible_solution=state.get("possible_solution", ""),
        requires_ticket=state.get("requires_ticket", False),
        ticket_id=state.get("ticket_id") or "",
        clarifying_question=state.get("clarifying_question") or "",
    )
