# Agentic Support Orchestrator

Prototipo local para orquestar agentes de soporte TI con LangGraph, LangChain y DeepSeek Reasoner.
La aplicacion puede ejecutarse localmente o con Docker; solo el modelo de IA usa la API de DeepSeek mediante `DEEPSEEK_API_KEY`.

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
python -m app.main
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
