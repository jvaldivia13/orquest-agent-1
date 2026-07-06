import json
from datetime import datetime
from pathlib import Path
from typing import Any


def append_interaction_log(state: dict[str, Any], log_path: Path | None = None) -> None:
    path = log_path or Path("logs/interactions.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "request_id": state.get("request_id"),
        "timestamp": datetime.now().isoformat(),
        "detected_category": state.get("category"),
        "priority": state.get("priority"),
        "requires_ticket": state.get("requires_ticket"),
        "needs_more_info": state.get("needs_more_info"),
        "ticket_id": state.get("ticket_id"),
        "validation_status": state.get("validation_status"),
        "error_message": state.get("error_message"),
    }
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
