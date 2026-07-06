from fastapi import FastAPI
from pydantic import BaseModel, Field

from graph.support_graph import support_graph


app = FastAPI(title="Agentic Support Orchestrator")


class SupportRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


@app.post("/support/request")
def create_support_request(request: SupportRequest) -> dict:
    result = support_graph.invoke({"user_message": request.message})

    return {
        "category": result.get("category"),
        "priority": result.get("priority"),
        "requires_ticket": result.get("requires_ticket"),
        "ticket_id": result.get("ticket_id"),
        "response": result.get("final_response"),
    }
