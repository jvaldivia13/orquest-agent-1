from concurrent.futures import ThreadPoolExecutor

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


def test_create_support_ticket_ids_are_unique_under_concurrency():
    def create_one(_index):
        return create_support_ticket(
            category="Software",
            description="Aplicacion falla",
            priority="Media",
        )["ticket_id"]

    with ThreadPoolExecutor(max_workers=20) as executor:
        ticket_ids = list(executor.map(create_one, range(100)))

    assert len(ticket_ids) == len(set(ticket_ids))
