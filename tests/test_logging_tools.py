import json

from tools.logging_tools import append_interaction_log


def test_append_interaction_log_writes_safe_jsonl(tmp_path):
    log_path = tmp_path / "interactions.jsonl"
    state = {
        "request_id": "REQ-1",
        "user_message": "Mi contraseña es secreta",
        "category": "Acceso / autenticación",
        "priority": "Media",
        "requires_ticket": True,
        "ticket_id": "INC-1",
        "validation_status": True,
        "error_message": None,
    }

    append_interaction_log(state, log_path=log_path)

    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert record["request_id"] == "REQ-1"
    assert "user_message" not in record
    assert record["ticket_id"] == "INC-1"
