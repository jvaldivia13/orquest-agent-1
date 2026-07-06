# Agentic Support Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local/Docker prototype that receives IT support requests, classifies them, searches a local KB, decides whether to answer or create a simulated ticket, validates the response, and exposes CLI plus optional FastAPI execution while consuming DeepSeek through its API.

**Architecture:** Keep LangGraph as the workflow coordinator and keep each agent as a focused Python node that mutates `SupportState`. DeepSeek access is isolated behind `llm/deepseek_client.py` and a small LLM service layer so nodes can fall back to deterministic local rules when the API is unavailable or tests run without credentials. Local tools own KB search, ticket creation, and interaction logging.

**Tech Stack:** Python 3.11+, LangGraph, LangChain, `langchain-deepseek`, FastAPI, Uvicorn, Pydantic, pytest, Docker, Docker Compose.

---

## File Structure

- Modify `graph/state.py`: add explicit fields for ambiguity, retry limits, logging, execution status, and request metadata.
- Modify `graph/routing.py`: route resolver decisions to ticketing, direct response, or clarification response.
- Modify `graph/support_graph.py`: wire the new conditional routes and keep graph construction isolated.
- Create `llm/support_llm.py`: provide structured classification and response helper functions using DeepSeek with deterministic fallbacks.
- Modify `agents/classifier_agent.py`: replace hardcoded classification with LLM-assisted classification plus local keyword fallback.
- Modify `agents/knowledge_agent.py`: keep node small and delegate ranking to the KB tool.
- Modify `tools/knowledge_tools.py`: implement keyword scoring, malformed JSON handling, and stable result ordering.
- Modify `data/knowledge_base.json`: add `keywords` arrays to support local relevance scoring.
- Modify `agents/resolver_agent.py`: set `requires_ticket`, `needs_more_info`, `resolution_decision`, and priority.
- Modify `agents/response_agent.py`: build normal, ticket, error, and clarification responses.
- Modify `agents/validator_agent.py`: add validation retry limit and controlled fallback response.
- Create `tools/logging_tools.py`: append safe interaction summaries to `logs/interactions.jsonl`.
- Modify `app/main.py` and `app/api.py`: validate input length and return useful response metadata.
- Modify `tests/*`: expand unit and graph tests to cover the functional requirements.
- Modify `README.md`: document local setup, DeepSeek API configuration, CLI, API, Docker, and tests.

---

### Task 1: Installable Test Harness

**Files:**
- Modify: `requirements.txt`
- Modify: `README.md`

- [ ] **Step 1: Confirm dependencies are listed**

Ensure `requirements.txt` contains:

```txt
langchain
langgraph
langchain-deepseek
python-dotenv
pydantic
fastapi
uvicorn
pytest
```

- [ ] **Step 2: Install dependencies in a virtual environment**

Run:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Expected: packages install successfully.

- [ ] **Step 3: Run the current tests**

Run:

```bash
python -m pytest -q
```

Expected before implementation: tests either pass or fail with explicit missing behavior from the current skeleton. A failure caused by missing `DEEPSEEK_API_KEY` is not acceptable and must be fixed by fallback logic before continuing.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt README.md
git commit -m "chore: prepare test harness"
```

---

### Task 2: Expand Shared State

**Files:**
- Modify: `graph/state.py`
- Test: `tests/test_state_contract.py`

- [ ] **Step 1: Write the state contract test**

Create `tests/test_state_contract.py`:

```python
from graph.state import SupportState


def test_support_state_accepts_required_flow_fields():
    state: SupportState = {
        "request_id": "REQ-1",
        "user_message": "Tengo un problema",
        "category": "Otro",
        "priority": "Media",
        "requires_ticket": False,
        "needs_more_info": True,
        "clarifying_question": "¿Puedes indicar qué componente falla?",
        "validation_retry_count": 0,
        "max_validation_retries": 2,
        "resolution_decision": "Solicitar más información.",
    }

    assert state["needs_more_info"] is True
    assert state["max_validation_retries"] == 2
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python -m pytest tests/test_state_contract.py -q
```

Expected: fail because the new typed fields are not declared.

- [ ] **Step 3: Update `graph/state.py`**

Replace the class body with:

```python
from typing import List, Optional, TypedDict


class SupportState(TypedDict, total=False):
    request_id: str
    user_message: str

    category: str
    priority: str
    requires_ticket: bool
    needs_more_info: bool
    clarifying_question: Optional[str]
    resolution_decision: str

    knowledge_results: List[str]
    possible_solution: str

    ticket_id: Optional[str]
    ticket_status: Optional[str]

    draft_response: str
    final_response: str

    validation_status: bool
    validation_feedback: Optional[str]
    validation_retry_count: int
    max_validation_retries: int

    error_message: Optional[str]
    interaction_logged: bool
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python -m pytest tests/test_state_contract.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add graph/state.py tests/test_state_contract.py
git commit -m "feat: expand support graph state"
```

---

### Task 3: Add KB Relevance Scoring

**Files:**
- Modify: `data/knowledge_base.json`
- Modify: `tools/knowledge_tools.py`
- Test: `tests/test_knowledge_tools.py`

- [ ] **Step 1: Add failing tests**

Replace `tests/test_knowledge_tools.py` with:

```python
from tools.knowledge_tools import search_knowledge_base


def test_search_knowledge_base_by_category():
    result = search_knowledge_base(
        category="Red / conectividad",
        user_message="No puedo conectarme a la VPN",
    )

    assert result["articles"]
    assert result["possible_solution"]


def test_search_knowledge_base_prioritizes_keywords():
    result = search_knowledge_base(
        category="Acceso / autenticación",
        user_message="No funciona mi MFA al iniciar sesión",
    )

    assert result["articles"][0]["id"] == "KB-004"
    assert "MFA" in result["possible_solution"]


def test_search_knowledge_base_unknown_category_returns_empty_result():
    result = search_knowledge_base(
        category="Categoría inexistente",
        user_message="Algo falla",
    )

    assert result == {"articles": [], "possible_solution": ""}
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_knowledge_tools.py -q
```

Expected: keyword prioritization fails because the current KB has no scoring.

- [ ] **Step 3: Update `data/knowledge_base.json`**

Use this content:

```json
[
  {
    "id": "KB-001",
    "category": "Acceso / autenticación",
    "title": "Problemas comunes de autenticación",
    "keywords": ["login", "cuenta", "contraseña", "bloqueada", "sesión"],
    "content": "Verificar si la cuenta está bloqueada o si la contraseña expiró."
  },
  {
    "id": "KB-004",
    "category": "Acceso / autenticación",
    "title": "Validación de MFA",
    "keywords": ["mfa", "autenticador", "factor", "código", "token"],
    "content": "Validar que el MFA esté activo, sincronizado y disponible en el dispositivo autorizado."
  },
  {
    "id": "KB-002",
    "category": "Red / conectividad",
    "title": "Problemas de conexión VPN",
    "keywords": ["vpn", "conexión", "internet", "red", "cliente"],
    "content": "Validar conexión a internet, estado del cliente VPN y credenciales corporativas."
  },
  {
    "id": "KB-003",
    "category": "Hardware",
    "title": "Problemas con periféricos",
    "keywords": ["laptop", "monitor", "teclado", "mouse", "periférico"],
    "content": "Validar conexión física, drivers instalados y estado del dispositivo en el administrador de dispositivos."
  },
  {
    "id": "KB-005",
    "category": "Software",
    "title": "Problemas con aplicaciones corporativas",
    "keywords": ["aplicación", "instalación", "software", "programa", "error"],
    "content": "Validar versión instalada, permisos, errores recientes y reinicio de la aplicación."
  }
]
```

- [ ] **Step 4: Implement scoring in `tools/knowledge_tools.py`**

Replace the file with:

```python
import json
from pathlib import Path
from typing import Any


def _score_article(article: dict[str, Any], user_message: str) -> int:
    message = user_message.lower()
    score = 0
    for keyword in article.get("keywords", []):
        if keyword.lower() in message:
            score += 2
    if article.get("title", "").lower() in message:
        score += 1
    return score


def search_knowledge_base(category: str, user_message: str) -> dict:
    kb_path = Path("data/knowledge_base.json")
    if not kb_path.exists():
        return {"articles": [], "possible_solution": ""}

    try:
        with kb_path.open("r", encoding="utf-8") as file:
            knowledge_base = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {"articles": [], "possible_solution": ""}

    matches = [
        article
        for article in knowledge_base
        if article.get("category", "").lower() == category.lower()
    ]
    if not matches:
        return {"articles": [], "possible_solution": ""}

    ranked = sorted(
        matches,
        key=lambda article: (_score_article(article, user_message), article.get("id", "")),
        reverse=True,
    )
    return {
        "articles": ranked,
        "possible_solution": ranked[0].get("content", ""),
    }
```

- [ ] **Step 5: Run tests**

Run:

```bash
python -m pytest tests/test_knowledge_tools.py -q
```

Expected: `3 passed`.

- [ ] **Step 6: Commit**

```bash
git add data/knowledge_base.json tools/knowledge_tools.py tests/test_knowledge_tools.py
git commit -m "feat: rank knowledge base results"
```

---

### Task 4: Implement Structured Classification With Fallback

**Files:**
- Create: `llm/support_llm.py`
- Modify: `agents/classifier_agent.py`
- Test: `tests/test_classifier.py`

- [ ] **Step 1: Write classifier tests**

Replace `tests/test_classifier.py` with:

```python
from agents.classifier_agent import classifier_node


def test_classifier_access_request():
    result = classifier_node({"user_message": "No puedo acceder a mi cuenta"})

    assert result["category"] == "Acceso / autenticación"
    assert result["priority"] == "Media"


def test_classifier_vpn_request():
    result = classifier_node({"user_message": "No puedo conectarme a la VPN"})

    assert result["category"] == "Red / conectividad"


def test_classifier_high_priority_for_massive_impact():
    result = classifier_node(
        {"user_message": "Toda la oficina está sin internet y no podemos trabajar"}
    )

    assert result["category"] == "Red / conectividad"
    assert result["priority"] == "Alta"


def test_classifier_unknown_request_goes_to_other():
    result = classifier_node({"user_message": "Tengo un problema extraño"})

    assert result["category"] == "Otro"
```

- [ ] **Step 2: Run tests to verify failures**

Run:

```bash
python -m pytest tests/test_classifier.py -q
```

Expected: high-priority detection fails with current implementation.

- [ ] **Step 3: Create `llm/support_llm.py`**

Add:

```python
import json
from typing import Any

from app.config import settings
from llm.deepseek_client import get_deepseek_reasoner


ALLOWED_CATEGORIES = {
    "Acceso / autenticación",
    "Red / conectividad",
    "Hardware",
    "Software",
    "Solicitud administrativa",
    "Otro",
}


def _fallback_classification(user_message: str) -> dict[str, str]:
    message = user_message.lower()
    category = "Otro"
    if any(term in message for term in ("login", "contraseña", "mfa", "cuenta", "sesión")):
        category = "Acceso / autenticación"
    elif any(term in message for term in ("vpn", "wi-fi", "wifi", "conexión", "internet", "red")):
        category = "Red / conectividad"
    elif any(term in message for term in ("laptop", "monitor", "teclado", "mouse", "pantalla")):
        category = "Hardware"
    elif any(term in message for term in ("aplicación", "instalación", "software", "programa", "error")):
        category = "Software"
    elif any(term in message for term in ("permiso", "aprobación", "solicito acceso")):
        category = "Solicitud administrativa"

    priority = "Alta" if any(term in message for term in ("toda la oficina", "masivo", "crítico", "urgente")) else "Media"
    return {"category": category, "priority": priority}


def classify_support_request(user_message: str) -> dict[str, str]:
    if not settings.DEEPSEEK_API_KEY:
        return _fallback_classification(user_message)

    prompt = (
        "Clasifica el requerimiento de soporte TI. "
        "Devuelve solo JSON con keys category y priority. "
        "Categorías permitidas: Acceso / autenticación, Red / conectividad, Hardware, "
        "Software, Solicitud administrativa, Otro. Prioridades: Baja, Media, Alta. "
        f"Mensaje: {user_message}"
    )
    try:
        response = get_deepseek_reasoner().invoke(prompt)
        content = getattr(response, "content", str(response))
        parsed: dict[str, Any] = json.loads(content)
        category = str(parsed.get("category", "Otro"))
        priority = str(parsed.get("priority", "Media")).capitalize()
    except Exception:
        return _fallback_classification(user_message)

    if category not in ALLOWED_CATEGORIES:
        category = "Otro"
    if priority not in {"Baja", "Media", "Alta"}:
        priority = "Media"
    return {"category": category, "priority": priority}
```

- [ ] **Step 4: Update `agents/classifier_agent.py`**

Replace with:

```python
from llm.support_llm import classify_support_request
from graph.state import SupportState


def classifier_node(state: SupportState) -> SupportState:
    classification = classify_support_request(state.get("user_message", ""))

    state["category"] = classification["category"]
    state["priority"] = classification["priority"]
    state["requires_ticket"] = False
    state["needs_more_info"] = False
    return state
```

- [ ] **Step 5: Run tests**

Run:

```bash
python -m pytest tests/test_classifier.py -q
```

Expected: `4 passed`.

- [ ] **Step 6: Commit**

```bash
git add llm/support_llm.py agents/classifier_agent.py tests/test_classifier.py
git commit -m "feat: classify support requests with fallback"
```

---

### Task 5: Resolver Ambiguity and Ticket Decisions

**Files:**
- Modify: `agents/resolver_agent.py`
- Modify: `graph/routing.py`
- Modify: `graph/support_graph.py`
- Test: `tests/test_resolver.py`

- [ ] **Step 1: Write resolver tests**

Create `tests/test_resolver.py`:

```python
from agents.resolver_agent import resolver_node


def test_resolver_requests_more_info_for_ambiguous_message():
    result = resolver_node(
        {
            "category": "Otro",
            "priority": "Media",
            "user_message": "Tengo un problema con mi equipo",
            "possible_solution": "",
        }
    )

    assert result["needs_more_info"] is True
    assert result["requires_ticket"] is False
    assert result["clarifying_question"]


def test_resolver_creates_ticket_when_no_solution_for_clear_category():
    result = resolver_node(
        {
            "category": "Software",
            "priority": "Media",
            "user_message": "La aplicación contable falla",
            "possible_solution": "",
        }
    )

    assert result["requires_ticket"] is True
    assert result["needs_more_info"] is False


def test_resolver_creates_ticket_for_high_priority():
    result = resolver_node(
        {
            "category": "Red / conectividad",
            "priority": "Alta",
            "user_message": "Toda la oficina está sin internet",
            "possible_solution": "Validar conexión a internet.",
        }
    )

    assert result["requires_ticket"] is True
```

- [ ] **Step 2: Run tests to verify failures**

Run:

```bash
python -m pytest tests/test_resolver.py -q
```

Expected: ambiguity test fails because `needs_more_info` is not set.

- [ ] **Step 3: Replace `agents/resolver_agent.py`**

```python
from graph.state import SupportState


def resolver_node(state: SupportState) -> SupportState:
    category = state.get("category", "Otro")
    possible_solution = state.get("possible_solution", "")
    priority = state.get("priority", "Media")
    user_message = state.get("user_message", "").lower()

    state["needs_more_info"] = False
    state["requires_ticket"] = False
    state["clarifying_question"] = None

    if category == "Otro" and not possible_solution:
        state["needs_more_info"] = True
        state["resolution_decision"] = "Solicitar más información por solicitud ambigua."
        state["clarifying_question"] = (
            "¿Puedes indicar qué servicio, aplicación, dispositivo o acceso presenta el problema?"
        )
        return state

    if not possible_solution:
        state["requires_ticket"] = True
        state["resolution_decision"] = "Crear ticket simulado por ausencia de solución conocida."
        return state

    if priority.lower() == "alta":
        state["requires_ticket"] = True
        state["resolution_decision"] = "Crear ticket simulado por prioridad alta."
        return state

    if any(term in user_message for term in ("bloqueada", "bloqueo", "mfa", "seguridad")):
        state["requires_ticket"] = True
        state["resolution_decision"] = "Crear ticket simulado por posible caso de seguridad o credenciales."
        return state

    state["resolution_decision"] = "Responder automáticamente con solución conocida."
    return state
```

- [ ] **Step 4: Replace `graph/routing.py`**

```python
from langgraph.graph import END

from graph.state import SupportState


def route_after_resolver(state: SupportState) -> str:
    if state.get("needs_more_info"):
        return "response"
    if state.get("requires_ticket"):
        return "ticketing"
    return "response"


def route_after_validator(state: SupportState) -> str:
    if state.get("validation_status"):
        return END
    if state.get("validation_retry_count", 0) >= state.get("max_validation_retries", 2):
        return END
    return "response"
```

- [ ] **Step 5: Run resolver tests**

Run:

```bash
python -m pytest tests/test_resolver.py -q
```

Expected: `3 passed`.

- [ ] **Step 6: Commit**

```bash
git add agents/resolver_agent.py graph/routing.py tests/test_resolver.py
git commit -m "feat: resolve ambiguity and ticket decisions"
```

---

### Task 6: Response Builder and Validator Retry Limit

**Files:**
- Modify: `agents/response_agent.py`
- Modify: `agents/validator_agent.py`
- Test: `tests/test_response.py`
- Test: `tests/test_validator.py`

- [ ] **Step 1: Write response tests**

Create `tests/test_response.py`:

```python
from agents.response_agent import response_node


def test_response_asks_clarifying_question():
    result = response_node(
        {
            "category": "Otro",
            "needs_more_info": True,
            "clarifying_question": "¿Qué componente falla?",
        }
    )

    assert "necesitamos un poco más de información" in result["draft_response"]
    assert "¿Qué componente falla?" in result["draft_response"]


def test_response_does_not_claim_ticket_without_ticket_id():
    result = response_node(
        {
            "category": "Software",
            "requires_ticket": True,
            "possible_solution": "",
        }
    )

    assert "no se pudo generar el ticket" in result["draft_response"]
    assert "Se ha generado el ticket" not in result["draft_response"]
```

- [ ] **Step 2: Replace validator tests**

Replace `tests/test_validator.py` with:

```python
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
```

- [ ] **Step 3: Run tests to verify failures**

Run:

```bash
python -m pytest tests/test_response.py tests/test_validator.py -q
```

Expected: retry and clarification tests fail.

- [ ] **Step 4: Replace `agents/response_agent.py`**

```python
from graph.state import SupportState


def response_node(state: SupportState) -> SupportState:
    if state.get("needs_more_info"):
        question = state.get("clarifying_question") or "¿Puedes compartir más detalle del problema?"
        state["draft_response"] = (
            "Para ayudarte correctamente, necesitamos un poco más de información.\n\n"
            f"{question}"
        )
        return state

    category = state.get("category", "Otro")
    possible_solution = state.get("possible_solution", "")
    requires_ticket = state.get("requires_ticket", False)
    ticket_id = state.get("ticket_id")

    response = f"Hemos identificado que tu solicitud está relacionada con {category}.\n\n"

    if possible_solution:
        response += f"Recomendación inicial: {possible_solution}\n\n"

    if requires_ticket and ticket_id:
        response += f"Se ha generado el ticket simulado {ticket_id} para seguimiento."
    elif requires_ticket:
        response += "El caso requiere soporte, pero no se pudo generar el ticket simulado."
    else:
        response += "Puedes seguir los pasos indicados. Si el problema continúa, contacta al equipo de soporte."

    state["draft_response"] = response
    return state
```

- [ ] **Step 5: Replace `agents/validator_agent.py`**

```python
from graph.state import SupportState


def _fail(state: SupportState, feedback: str) -> SupportState:
    retry_count = state.get("validation_retry_count", 0) + 1
    max_retries = state.get("max_validation_retries", 2)
    state["validation_retry_count"] = retry_count
    state["validation_feedback"] = feedback

    if retry_count > max_retries:
        state["validation_status"] = True
        state["final_response"] = (
            "No pudimos construir una respuesta validada automáticamente. "
            "Por favor, intenta describir el problema con más detalle."
        )
    else:
        state["validation_status"] = False
    return state


def validator_node(state: SupportState) -> SupportState:
    state.setdefault("validation_retry_count", 0)
    state.setdefault("max_validation_retries", 2)

    draft_response = state.get("draft_response", "")
    requires_ticket = state.get("requires_ticket", False)
    ticket_id = state.get("ticket_id")

    if not draft_response:
        return _fail(state, "La respuesta está vacía.")

    if "contraseña" in draft_response.lower() and "comparte" in draft_response.lower():
        return _fail(state, "La respuesta podría solicitar datos sensibles.")

    if requires_ticket and ticket_id and ticket_id not in draft_response:
        return _fail(state, "La respuesta no incluye el ticket generado.")

    state["validation_status"] = True
    state["final_response"] = draft_response
    return state
```

- [ ] **Step 6: Run tests**

Run:

```bash
python -m pytest tests/test_response.py tests/test_validator.py -q
```

Expected: `5 passed`.

- [ ] **Step 7: Commit**

```bash
git add agents/response_agent.py agents/validator_agent.py tests/test_response.py tests/test_validator.py
git commit -m "feat: build and validate safe responses"
```

---

### Task 7: Interaction Logging

**Files:**
- Create: `tools/logging_tools.py`
- Modify: `graph/support_graph.py`
- Test: `tests/test_logging_tools.py`

- [ ] **Step 1: Write logging tests**

Create `tests/test_logging_tools.py`:

```python
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
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
python -m pytest tests/test_logging_tools.py -q
```

Expected: fail because `tools.logging_tools` does not exist.

- [ ] **Step 3: Create `tools/logging_tools.py`**

```python
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
```

- [ ] **Step 4: Add log node in `graph/support_graph.py`**

Add:

```python
from tools.logging_tools import append_interaction_log


def log_interaction_node(state: SupportState) -> SupportState:
    append_interaction_log(state)
    state["interaction_logged"] = True
    return state
```

Then add the log node:

```python
workflow.add_node("log_interaction", log_interaction_node)
```

Replace the validator conditional edge with this exact route:

```python
workflow.add_conditional_edges(
    "validator",
    route_after_validator,
    {
        "response": "response",
        "log_interaction": "log_interaction",
    },
)
workflow.add_edge("log_interaction", END)
```

Replace `route_after_validator()` in `graph/routing.py` with:

```python
def route_after_validator(state: SupportState) -> str:
    if state.get("validation_status"):
        return "log_interaction"
    if state.get("validation_retry_count", 0) >= state.get("max_validation_retries", 2):
        return "log_interaction"
    return "response"
```

- [ ] **Step 5: Run logging tests**

Run:

```bash
python -m pytest tests/test_logging_tools.py -q
```

Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add tools/logging_tools.py graph/support_graph.py tests/test_logging_tools.py
git commit -m "feat: log support interactions"
```

---

### Task 8: End-to-End Graph Coverage

**Files:**
- Modify: `tests/test_graph.py`
- Modify: `graph/support_graph.py`

- [ ] **Step 1: Replace graph tests**

Replace `tests/test_graph.py` with:

```python
from graph.support_graph import support_graph


def test_graph_returns_final_response_for_known_solution():
    result = support_graph.invoke({"user_message": "No puedo conectarme a la VPN"})

    assert result["final_response"]
    assert result["category"] == "Red / conectividad"
    assert result["requires_ticket"] is False


def test_graph_creates_ticket_for_mfa_issue():
    result = support_graph.invoke({"user_message": "No funciona mi MFA"})

    assert result["category"] == "Acceso / autenticación"
    assert result["requires_ticket"] is True
    assert result["ticket_id"].startswith("INC-")
    assert result["ticket_id"] in result["final_response"]


def test_graph_asks_more_info_for_ambiguous_request():
    result = support_graph.invoke({"user_message": "Tengo un problema con mi equipo"})

    assert result["needs_more_info"] is True
    assert "más de información" in result["final_response"]
```

- [ ] **Step 2: Run graph tests**

Run:

```bash
python -m pytest tests/test_graph.py -q
```

Expected: the test fails only when the final graph shape has not yet been applied.

- [ ] **Step 3: Apply final graph wiring**

Use this final graph shape:

```python
workflow.add_edge("classifier", "knowledge")
workflow.add_edge("knowledge", "resolver")
workflow.add_conditional_edges(
    "resolver",
    route_after_resolver,
    {"ticketing": "ticketing", "response": "response"},
)
workflow.add_edge("ticketing", "response")
workflow.add_edge("response", "validator")
workflow.add_conditional_edges(
    "validator",
    route_after_validator,
    {"response": "response", "log_interaction": "log_interaction"},
)
workflow.add_edge("log_interaction", END)
```

Update `route_after_validator()` to return `"log_interaction"` for valid responses.

- [ ] **Step 4: Run graph tests again**

Run:

```bash
python -m pytest tests/test_graph.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add graph/support_graph.py graph/routing.py tests/test_graph.py
git commit -m "test: cover support graph flows"
```

---

### Task 9: CLI and API Input Validation

**Files:**
- Modify: `app/main.py`
- Modify: `app/api.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write API tests**

Create `tests/test_api.py`:

```python
from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_support_request_rejects_empty_message():
    response = client.post("/support/request", json={"message": ""})

    assert response.status_code == 422


def test_support_request_returns_response():
    response = client.post(
        "/support/request",
        json={"message": "No puedo conectarme a la VPN"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Red / conectividad"
    assert body["response"]
```

- [ ] **Step 2: Run API tests**

Run:

```bash
python -m pytest tests/test_api.py -q
```

Expected: pass if graph dependencies are installed; otherwise dependency error identifies missing package installation.

- [ ] **Step 3: Update `app/main.py` for empty input**

Replace `main()` with:

```python
def main() -> None:
    configure_logging()
    user_message = input("Ingrese su requerimiento: ").strip()
    if not user_message:
        print("Debes ingresar un requerimiento para continuar.")
        return
    if len(user_message) > 2000:
        print("El requerimiento supera el máximo permitido de 2000 caracteres.")
        return

    result = support_graph.invoke({"user_message": user_message})

    print("\nRespuesta final:")
    print(result.get("final_response", "No se pudo generar una respuesta final."))
```

- [ ] **Step 4: Run API tests and compile CLI**

Run:

```bash
python -m pytest tests/test_api.py -q
python -m compileall app
```

Expected: API tests pass and compile exits with code 0.

- [ ] **Step 5: Commit**

```bash
git add app/main.py app/api.py tests/test_api.py
git commit -m "feat: validate cli and api input"
```

---

### Task 10: Documentation and Docker Verification

**Files:**
- Modify: `README.md`
- Modify: `Dockerfile`
- Modify: `docker-compose.yml`
- Modify: `.gitignore`

- [ ] **Step 1: Update `.gitignore`**

Ensure it contains:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
logs/*.log
logs/interactions.jsonl
```

- [ ] **Step 2: Update README sections**

Ensure `README.md` includes these commands:

```markdown
## Instalación local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Pruebas

```bash
python -m pytest -q
python -m compileall app graph agents llm tools prompts tests
```

## API local

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```
```

- [ ] **Step 3: Run full local verification**

Run:

```bash
python -m pytest -q
python -m compileall app graph agents llm tools prompts tests
```

Expected: all tests pass and compile exits with code 0.

- [ ] **Step 4: Run Docker build**

Run:

```bash
docker build -t agentic-support-orchestrator .
```

Expected: image builds successfully.

- [ ] **Step 5: Commit**

```bash
git add README.md Dockerfile docker-compose.yml .gitignore
git commit -m "docs: document local and docker execution"
```

---

## Self-Review

- **Spec coverage:** RF-001 through RF-012 are covered by tasks for CLI/API input, classifier, KB, resolver, ticketing, response builder, validator, logging, Docker, and extensible state/graph structure.
- **Known dependency:** tests require installing `pytest`, `langgraph`, `fastapi`, and related packages from `requirements.txt`; the current global Python may not have them.
- **DeepSeek boundary:** DeepSeek API access remains isolated behind `llm/deepseek_client.py` and `llm/support_llm.py`; fallback logic keeps local tests independent from API credentials.
- **Ambiguity coverage:** Task 5 and Task 8 cover `needs_more_info` and clarification responses.
- **Validation loop coverage:** Task 6 adds retry limits and prevents infinite validator loops.
- **Logging coverage:** Task 7 defines safe JSONL logging without storing raw `user_message`.
- **No placeholders:** Every implementation task includes concrete file paths, code blocks, commands, and expected outcomes.
