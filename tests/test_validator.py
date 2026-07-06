from agents.validator_agent import validator_node


def test_validator_accepts_response_with_ticket():
    result = validator_node(
        {
            "draft_response": "Se ha generado el ticket simulado INC-1.",
            "requires_ticket": True,
            "ticket_id": "INC-1",
        }
    )

    assert result["validation_status"] is True
    assert result["final_response"]
