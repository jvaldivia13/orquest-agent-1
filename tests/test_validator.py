from agents.validator_agent import validator_node


def test_validator_accepts_response_with_ticket():
    result = validator_node(
        {
            "draft_response": "Se ha generado el ticket simulado INC-1.",
            "requires_ticket": True,
            "ticket_id": "INC-1",
            "validation_retry_count": 0,
            "max_validation_retries": 2,
        }
    )

    assert result["validation_status"] is True
    assert result["final_response"]


def test_validator_fails_without_required_ticket_id_and_increments_retry():
    result = validator_node(
        {
            "draft_response": "Se ha generado el ticket simulado.",
            "requires_ticket": True,
            "ticket_id": "INC-9",
            "validation_retry_count": 0,
            "max_validation_retries": 2,
        }
    )

    assert result["validation_status"] is False
    assert result["validation_retry_count"] == 1


def test_validator_stops_with_controlled_response_after_max_retries():
    result = validator_node(
        {
            "draft_response": "",
            "requires_ticket": False,
            "validation_retry_count": 2,
            "max_validation_retries": 2,
        }
    )

    assert result["validation_status"] is True
    assert "No pudimos construir" in result["final_response"]
