from tools.ticketing_tools import create_support_ticket


def test_create_support_ticket():
    result = create_support_ticket(
        category="Acceso / autenticación",
        description="No puedo acceder",
        priority="Media",
    )

    assert result["ticket_id"].startswith("INC-")
    assert result["status"] == "Created"


def test_create_support_ticket_generates_unique_ids_for_rapid_requests():
    tickets = [
        create_support_ticket(
            category="Acceso / autenticaciÃ³n",
            description="No puedo acceder",
            priority="Media",
        )
        for _ in range(5)
    ]

    ticket_ids = [ticket["ticket_id"] for ticket in tickets]
    assert len(ticket_ids) == len(set(ticket_ids))
