# LLM Hardening And Agent Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the implemented agents with the intended LangChain/DeepSeek architecture, remove dead prompt code, harden LLM JSON parsing, fix concurrent ticket ID generation, and stabilize dependencies.

**Architecture:** Keep the current LangGraph topology and local-first behavior. DeepSeek usage becomes explicit, testable, and observable through small LLM helper functions with deterministic Python fallbacks when the API key is missing or the model response is invalid.

**Tech Stack:** Python 3.11+, LangGraph, LangChain, `langchain-deepseek`, FastAPI, pytest, Docker.

---

## Scope Decision

Use the existing prompt modules instead of deleting them. The functional/technical requirements describe LangChain + DeepSeek as part of the agentic flow, so the better correction is to make prompts live and keep deterministic fallbacks for local/offline execution.

## File Structure

- Modify `prompts/classifier_prompt.py`: expose a formatter used by the classifier.
- Modify `prompts/resolver_prompt.py`: expose a formatter for resolver LLM decisions.
- Modify `prompts/response_prompt.py`: expose a formatter for final response generation.
- Modify `prompts/validator_prompt.py`: expose a formatter for validation.
- Modify `llm/deepseek_client.py`: optionally support model kwargs such as JSON response format if supported.
- Modify `llm/support_llm.py`: add robust JSON extraction/parsing and LLM helper functions.
- Modify `agents/resolver_agent.py`: call LLM-assisted resolver when configured, fallback to current rules.
- Modify `agents/response_agent.py`: call LLM-assisted response builder when configured, fallback to current template.
- Modify `agents/validator_agent.py`: call LLM-assisted validator when configured, fallback to current rules.
- Modify `tools/ticketing_tools.py`: replace global timestamp race with thread-safe ID generation.
- Modify `requirements.txt`: pin dependency versions or minimum compatible versions.
- Modify tests under `tests/`: cover parsing, prompt usage, fallback behavior, ticket concurrency, and dependency file expectations.

---

### Task 1: Make Classifier Prompt Live And Harden JSON Parsing

**Files:**
- Modify: `prompts/classifier_prompt.py`
- Modify: `llm/support_llm.py`
- Test: `tests/test_deepseek_client.py`
- Test: `tests/test_classifier.py`

- [ ] **Step 1: Write failing tests for fenced JSON parsing**

Add to `tests/test_deepseek_client.py`:

```python
from llm.support_llm import parse_llm_json_object


def test_parse_llm_json_object_accepts_plain_json():
    assert parse_llm_json_object('{"category":"Software","priority":"Alta"}') == {
        "category": "Software",
        "priority": "Alta",
    }


def test_parse_llm_json_object_accepts_fenced_json():
    content = '```json\n{"category":"Hardware","priority":"Media"}\n```'

    assert parse_llm_json_object(content) == {
        "category": "Hardware",
        "priority": "Media",
    }
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python -m pytest tests/test_deepseek_client.py::test_parse_llm_json_object_accepts_plain_json tests/test_deepseek_client.py::test_parse_llm_json_object_accepts_fenced_json -q
```

Expected: FAIL because `parse_llm_json_object` does not exist.

- [ ] **Step 3: Implement robust JSON helper**

Add to `llm/support_llm.py`:

```python
def parse_llm_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("LLM response does not contain a JSON object")

    parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON is not an object")
    return parsed
```

- [ ] **Step 4: Update classifier to use `CLASSIFIER_PROMPT`**

In `prompts/classifier_prompt.py`, expose a function:

```python
CLASSIFIER_PROMPT = (
    "Clasifica el requerimiento de soporte TI. "
    "Devuelve solo JSON con keys category y priority. "
    "Categorias permitidas: Acceso / autenticacion, Red / conectividad, Hardware, "
    "Software, Solicitud administrativa, Otro. Prioridades: Baja, Media, Alta. "
    "Mensaje: {user_message}"
)


def build_classifier_prompt(user_message: str) -> str:
    return CLASSIFIER_PROMPT.format(user_message=user_message)
```

Update `classify_support_request()` to call `build_classifier_prompt(user_message)` and `parse_llm_json_object(content)`.

- [ ] **Step 5: Add silent fallback observability**

When LLM parsing fails, return fallback as today, but set a module-level logger warning:

```python
logger.warning("Falling back to local classification after invalid LLM response")
```

- [ ] **Step 6: Verify focused tests**

Run:

```bash
python -m pytest tests/test_deepseek_client.py tests/test_classifier.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add prompts/classifier_prompt.py llm/support_llm.py tests/test_deepseek_client.py tests/test_classifier.py
git commit -m "fix: harden llm classification parsing"
```

---

### Task 2: Add LLM-Assisted Resolver With Rule Fallback

**Files:**
- Modify: `prompts/resolver_prompt.py`
- Modify: `llm/support_llm.py`
- Modify: `agents/resolver_agent.py`
- Test: `tests/test_resolver.py`

- [ ] **Step 1: Write failing test for LLM resolver decision**

Add to `tests/test_resolver.py`:

```python
from agents import resolver_agent


def test_resolver_uses_llm_decision_when_available(monkeypatch):
    def fake_decision(_state):
        return {
            "requires_ticket": True,
            "needs_more_info": False,
            "resolution_decision": "Crear ticket por impacto reportado.",
            "clarifying_question": None,
        }

    monkeypatch.setattr(resolver_agent, "resolve_support_request", fake_decision)

    result = resolver_agent.resolver_node(
        {
            "category": "Software",
            "priority": "Media",
            "possible_solution": "Reiniciar aplicacion.",
            "user_message": "La aplicacion critica falla para el cierre",
        }
    )

    assert result["requires_ticket"] is True
    assert result["resolution_decision"] == "Crear ticket por impacto reportado."
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_resolver.py::test_resolver_uses_llm_decision_when_available -q
```

Expected: FAIL because `resolver_agent.resolve_support_request` is not imported/called.

- [ ] **Step 3: Implement resolver prompt formatter**

In `prompts/resolver_prompt.py`:

```python
RESOLVER_PROMPT = (
    "Evalua esta solicitud de soporte TI y devuelve solo JSON con keys "
    "requires_ticket, needs_more_info, resolution_decision y clarifying_question. "
    "Categoria: {category}. Prioridad: {priority}. Solucion conocida: {possible_solution}. "
    "Mensaje: {user_message}"
)


def build_resolver_prompt(state: dict) -> str:
    return RESOLVER_PROMPT.format(
        category=state.get("category", "Otro"),
        priority=state.get("priority", "Media"),
        possible_solution=state.get("possible_solution", ""),
        user_message=state.get("user_message", ""),
    )
```

- [ ] **Step 4: Add LLM resolver helper**

In `llm/support_llm.py`, add `resolve_support_request(state: dict) -> dict[str, Any]` that returns `{}` when `DEEPSEEK_API_KEY` is missing, invokes DeepSeek otherwise, parses JSON with `parse_llm_json_object`, and normalizes booleans.

- [ ] **Step 5: Integrate into resolver agent**

At the top of `agents/resolver_agent.py`:

```python
from llm.support_llm import resolve_support_request
```

At the start of `resolver_node`, call the helper. If it returns a non-empty dict with valid keys, apply it to state and return. If it returns `{}` or raises, continue with the existing rule-based logic.

- [ ] **Step 6: Verify resolver tests**

Run:

```bash
python -m pytest tests/test_resolver.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add prompts/resolver_prompt.py llm/support_llm.py agents/resolver_agent.py tests/test_resolver.py
git commit -m "feat: add llm-assisted resolver fallback"
```

---

### Task 3: Add LLM-Assisted Response Builder With Template Fallback

**Files:**
- Modify: `prompts/response_prompt.py`
- Modify: `llm/support_llm.py`
- Modify: `agents/response_agent.py`
- Test: `tests/test_response.py`

- [ ] **Step 1: Write failing test for LLM response usage**

Add to `tests/test_response.py`:

```python
from agents import response_agent


def test_response_uses_llm_text_when_available(monkeypatch):
    monkeypatch.setattr(
        response_agent,
        "build_support_response",
        lambda _state: "Respuesta generada por DeepSeek.",
    )

    result = response_agent.response_node(
        {
            "category": "Red / conectividad",
            "possible_solution": "Reiniciar cliente VPN.",
            "requires_ticket": False,
        }
    )

    assert result["draft_response"] == "Respuesta generada por DeepSeek."
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_response.py::test_response_uses_llm_text_when_available -q
```

Expected: FAIL because `response_agent.build_support_response` is not imported/called.

- [ ] **Step 3: Implement response prompt formatter**

In `prompts/response_prompt.py`, expose `build_response_prompt(state: dict) -> str` that includes category, solution, ticket status, ticket id, clarifying question, and user message.

- [ ] **Step 4: Add LLM response helper**

In `llm/support_llm.py`, add `build_support_response(state: dict) -> str` that returns `""` without API key and otherwise invokes DeepSeek. The helper should return plain text, not JSON.

- [ ] **Step 5: Integrate into response agent**

At the beginning of `response_node`, call `build_support_response(state)`. If it returns non-empty text, store it in `state["draft_response"]` and return. Otherwise continue with the existing deterministic response code.

- [ ] **Step 6: Verify response tests**

Run:

```bash
python -m pytest tests/test_response.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add prompts/response_prompt.py llm/support_llm.py agents/response_agent.py tests/test_response.py
git commit -m "feat: add llm-assisted response builder"
```

---

### Task 4: Add LLM-Assisted Validator With Rule Fallback

**Files:**
- Modify: `prompts/validator_prompt.py`
- Modify: `llm/support_llm.py`
- Modify: `agents/validator_agent.py`
- Test: `tests/test_validator.py`

- [ ] **Step 1: Write failing test for LLM validation usage**

Add to `tests/test_validator.py`:

```python
from agents import validator_agent


def test_validator_uses_llm_validation_when_available(monkeypatch):
    monkeypatch.setattr(
        validator_agent,
        "validate_support_response",
        lambda _state: {"validation_status": True, "validation_feedback": None},
    )

    result = validator_agent.validator_node(
        {
            "draft_response": "Respuesta clara.",
            "requires_ticket": False,
        }
    )

    assert result["validation_status"] is True
    assert result["final_response"] == "Respuesta clara."
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_validator.py::test_validator_uses_llm_validation_when_available -q
```

Expected: FAIL because the validator does not call the LLM helper.

- [ ] **Step 3: Implement validator prompt formatter**

In `prompts/validator_prompt.py`, expose `build_validator_prompt(state: dict) -> str` asking for JSON with `validation_status` and `validation_feedback`.

- [ ] **Step 4: Add LLM validator helper**

In `llm/support_llm.py`, add `validate_support_response(state: dict) -> dict[str, Any]`. It should return `{}` without API key or invalid output. It should parse JSON through `parse_llm_json_object`.

- [ ] **Step 5: Integrate into validator agent**

At the start of `validator_node`, call `validate_support_response(state)`. If it returns a dict containing `validation_status`, apply it. If valid, set `final_response = draft_response`. If invalid, set `validation_feedback` and let existing retry routing work. If helper returns `{}`, continue with existing rule-based validation.

- [ ] **Step 6: Verify validator tests**

Run:

```bash
python -m pytest tests/test_validator.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add prompts/validator_prompt.py llm/support_llm.py agents/validator_agent.py tests/test_validator.py
git commit -m "feat: add llm-assisted response validation"
```

---

### Task 5: Fix Concurrent Ticket ID Generation

**Files:**
- Modify: `tools/ticketing_tools.py`
- Test: `tests/test_ticketing.py`

- [ ] **Step 1: Write concurrent uniqueness test**

Add to `tests/test_ticketing.py`:

```python
from concurrent.futures import ThreadPoolExecutor

from tools.ticketing_tools import create_support_ticket


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
```

- [ ] **Step 2: Run test to expose race risk**

Run:

```bash
python -m pytest tests/test_ticketing.py::test_create_support_ticket_ids_are_unique_under_concurrency -q
```

Expected: may fail intermittently with current implementation. If it passes, proceed because the code review finding is still valid.

- [ ] **Step 3: Replace timestamp global with UUID**

In `tools/ticketing_tools.py`, simplify ID generation:

```python
from datetime import datetime
from uuid import uuid4


def create_support_ticket(category: str, description: str, priority: str) -> dict:
    now = datetime.now()
    ticket_id = f"INC-{now.strftime('%Y%m%d')}-{uuid4().hex[:12].upper()}"

    return {
        "ticket_id": ticket_id,
        "status": "Created",
        "category": category,
        "priority": priority,
        "description": description,
        "created_at": now.isoformat(),
    }
```

- [ ] **Step 4: Verify ticketing tests**

Run:

```bash
python -m pytest tests/test_ticketing.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/ticketing_tools.py tests/test_ticketing.py
git commit -m "fix: make ticket ids concurrency safe"
```

---

### Task 6: Pin Dependencies

**Files:**
- Modify: `requirements.txt`
- Optionally create: `requirements.lock`
- Test: `tests/test_requirements.py`

- [ ] **Step 1: Add test that key dependencies are pinned**

Create `tests/test_requirements.py`:

```python
from pathlib import Path


def test_runtime_dependencies_are_pinned():
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()
    runtime_packages = [
        "langchain",
        "langgraph",
        "langchain-deepseek",
        "python-dotenv",
        "pydantic",
        "fastapi",
        "uvicorn",
        "pytest",
    ]

    for package in runtime_packages:
        line = next((item for item in requirements if item.startswith(package)), "")
        assert "==" in line or "~=" in line or ">=" in line
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_requirements.py -q
```

Expected: FAIL because `requirements.txt` currently has unpinned package names.

- [ ] **Step 3: Pin versions**

Use installed versions from `.venv`:

```bash
python -m pip freeze | findstr /R "langchain langgraph langchain-deepseek python-dotenv pydantic fastapi uvicorn pytest"
```

Update `requirements.txt` with exact pins from the environment, for example:

```txt
fastapi==<installed>
langchain==<installed>
langchain-deepseek==<installed>
langgraph==<installed>
pydantic==<installed>
python-dotenv==<installed>
pytest==<installed>
uvicorn==<installed>
```

- [ ] **Step 4: Verify dependency test**

Run:

```bash
python -m pytest tests/test_requirements.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/test_requirements.py
git commit -m "chore: pin python dependencies"
```

---

### Task 7: Full Regression And Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/diagrams/orquestacion-agentes.md`

- [ ] **Step 1: Update README architecture notes**

Document:

```markdown
## Uso de DeepSeek

El sistema usa DeepSeek mediante LangChain cuando `DEEPSEEK_API_KEY` esta configurada.
Si la API no esta disponible o la respuesta no cumple el formato esperado, los agentes usan reglas locales de fallback.

Agentes con soporte LLM:
- Clasificador
- Resolutor
- Constructor de respuesta
- Validador
```

- [ ] **Step 2: Update orchestration diagram**

Add notes to `docs/diagrams/orquestacion-agentes.md` showing that resolver, response, and validator can use DeepSeek with local fallback.

- [ ] **Step 3: Run complete verification**

Run:

```bash
python -m pytest -q
python -m compileall app graph agents llm tools prompts tests
docker build -t agentic-support-orchestrator .
```

Expected:
- pytest passes.
- compileall exits 0.
- Docker build exits 0.

- [ ] **Step 4: Commit docs**

```bash
git add README.md docs/diagrams/orquestacion-agentes.md
git commit -m "docs: document llm agent fallbacks"
```

---

## Final Verification

After all tasks:

```bash
git status --short --branch
python -m pytest -q
python -m compileall app graph agents llm tools prompts tests
docker build -t agentic-support-orchestrator .
```

Expected:
- Working tree clean except intentional uncommitted work.
- All tests pass.
- Compileall exits 0.
- Docker build succeeds.

## Execution Options

1. **Subagent-Driven (recommended):** one focused worker per task with review between tasks.
2. **Inline Execution:** implement this plan in the current session using checkpoints.
