# Agentic Support Orchestrator

Prototipo local para orquestar agentes de soporte TI con LangGraph, LangChain y DeepSeek Reasoner.

## Requisitos

- Python 3.11+
- API Key de DeepSeek
- Docker opcional

## Instalación local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Configura `DEEPSEEK_API_KEY` en `.env`.

## Ejecución por consola

```bash
python app/main.py
```

## Ejecución API local

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest
```
