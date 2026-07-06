from datetime import datetime, timedelta


_last_ticket_timestamp: datetime | None = None


def _next_ticket_timestamp() -> datetime:
    global _last_ticket_timestamp

    now = datetime.now()
    if _last_ticket_timestamp is not None and now <= _last_ticket_timestamp:
        now = _last_ticket_timestamp + timedelta(microseconds=1)

    _last_ticket_timestamp = now
    return now


def create_support_ticket(category: str, description: str, priority: str) -> dict:
    now = _next_ticket_timestamp()
    ticket_id = f"INC-{now.strftime('%Y%m%d%H%M%S%f')}"

    return {
        "ticket_id": ticket_id,
        "status": "Created",
        "category": category,
        "priority": priority,
        "description": description,
        "created_at": now.isoformat(),
    }
