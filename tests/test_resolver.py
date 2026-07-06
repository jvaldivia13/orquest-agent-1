from agents.resolver_agent import resolver_node


def test_resolver_requests_more_info_for_ambiguous_message():
    result = resolver_node(
        {
            "category": "Otro",
            "priority": "Media",
            "user_message": "Tengo un problema con mi equipo",
            "possible_solution": "",
        }
    )

    assert result["needs_more_info"] is True
    assert result["requires_ticket"] is False
    assert result["clarifying_question"]


def test_resolver_creates_ticket_when_no_solution_for_clear_category():
    result = resolver_node(
        {
            "category": "Software",
            "priority": "Media",
            "user_message": "La aplicación contable falla",
            "possible_solution": "",
        }
    )

    assert result["requires_ticket"] is True
    assert result["needs_more_info"] is False


def test_resolver_creates_ticket_for_high_priority():
    result = resolver_node(
        {
            "category": "Red / conectividad",
            "priority": "Alta",
            "user_message": "Toda la oficina está sin internet",
            "possible_solution": "Validar conexión a internet.",
        }
    )

    assert result["requires_ticket"] is True
