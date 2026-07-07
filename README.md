# Agentic Support Orchestrator

Prototipo local para orquestar agentes de soporte TI con LangGraph, LangChain y DeepSeek Reasoner.
La aplicacion puede ejecutarse localmente o con Docker; solo el modelo de IA usa la API de DeepSeek mediante `DEEPSEEK_API_KEY`.

## Requisitos

- Python 3.11+
- API Key de DeepSeek
- Docker opcional

## Instalacion local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Configura `DEEPSEEK_API_KEY` en `.env`.

## Uso de DeepSeek

El sistema usa DeepSeek mediante LangChain cuando `DEEPSEEK_API_KEY` esta configurada.
Si la API no esta disponible o la respuesta no cumple el formato esperado, los agentes usan reglas locales de fallback.

Agentes con soporte LLM:

- Clasificador
- Resolutor
- Constructor de respuesta
- Validador

## Ejecucion por consola

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

Frontend de prueba:

```text
http://localhost:8000/
```

Documentacion interactiva:

```text
http://localhost:8000/docs
```

## Docker

```bash
docker compose up --build
```

Con Docker, el frontend queda disponible en `http://localhost:8000/`.
