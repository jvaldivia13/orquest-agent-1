from tools.ticketing_tools import create_support_ticket


def test_create_support_ticket():
    result = create_support_ticket(
        category="Acceso / autenticación",
        description="No puedo acceder",
        priority="Media",
    )

    assert result["ticket_id"].startswith("INC-")
    assert result["status"] == "Created"
