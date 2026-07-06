# Basic API Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal browser UI for testing the local support request API.

**Architecture:** FastAPI serves static files from `app/static` and returns `index.html` at `/`. Browser JavaScript submits JSON to the existing `/support/request` endpoint and renders the API response.

**Tech Stack:** FastAPI, Starlette static files, plain HTML, CSS, JavaScript, pytest.

---

### Task 1: Serve Frontend From FastAPI

**Files:**
- Modify: `tests/test_api.py`
- Modify: `app/api.py`
- Create: `app/static/index.html`
- Create: `app/static/styles.css`
- Create: `app/static/app.js`

- [ ] **Step 1: Write the failing test**

Add a test to `tests/test_api.py`:

```python
def test_root_serves_frontend():
    response = client.get("/")

    assert response.status_code == 200
    assert "Agentic Support Orchestrator" in response.text
    assert "/support/request" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_api.py::test_root_serves_frontend -q
```

Expected: FAIL because `/` is not implemented yet.

- [ ] **Step 3: Implement minimal frontend serving**

Update `app/api.py` to mount `/static` and serve `app/static/index.html` at `/`.

- [ ] **Step 4: Create frontend files**

Create `app/static/index.html`, `app/static/styles.css`, and `app/static/app.js`. The page must include the API path `/support/request` so the test and the UI both document the target endpoint.

- [ ] **Step 5: Run focused test**

Run:

```bash
python -m pytest tests/test_api.py::test_root_serves_frontend -q
```

Expected: PASS.

- [ ] **Step 6: Run full verification**

Run:

```bash
python -m pytest -q
python -m compileall app graph agents llm tools prompts tests
```

Expected: all tests pass and compileall exits with status 0.

- [ ] **Step 7: Update README**

Document that the browser frontend is available at `http://localhost:8000/` after starting Uvicorn or Docker.
