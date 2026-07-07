from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from graph.support_graph import support_graph


app = FastAPI(title="Agentic Support Orchestrator")
STATIC_DIR = Path(__file__).resolve().parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class SupportRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


@app.get("/")
def read_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/support/request")
def create_support_request(request: SupportRequest) -> dict:
    result = support_graph.invoke({"user_message": request.message})

    return {
        "category": result.get("category"),
        "priority": result.get("priority"),
        "requires_ticket": result.get("requires_ticket"),
        "ticket_id": result.get("ticket_id"),
        "knowledge_results": result.get("knowledge_results", []),
        "retrieval_mode": result.get("retrieval_mode"),
        "response": result.get("final_response"),
    }
