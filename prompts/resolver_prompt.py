RESOLVER_PROMPT = (
    "Evalua esta solicitud de soporte TI y devuelve solo JSON con keys "
    "requires_ticket, needs_more_info, resolution_decision y clarifying_question. "
    "Usa true/false para booleanos. "
    "Categoria: {category}. Prioridad: {priority}. Solucion conocida: {possible_solution}. "
    "Mensaje: {user_message}"
)


def build_resolver_prompt(state: dict) -> str:
    return RESOLVER_PROMPT.format(
        category=state.get("category", "Otro"),
        priority=state.get("priority", "Media"),
        possible_solution=state.get("possible_solution", ""),
        user_message=state.get("user_message", ""),
    )
