from datetime import datetime


def create_support_ticket(category: str, description: str, priority: str) -> dict:
    now = datetime.now()
    ticket_id = f"INC-{now.strftime('%Y%m%d%H%M%S')}"

    return {
        "ticket_id": ticket_id,
        "status": "Created",
        "category": category,
        "priority": priority,
        "description": description,
        "created_at": now.isoformat(),
    }
