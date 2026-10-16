# Week 10 — AI Agent Integration

## Overview

Week 10 extends the hospital AI/ML course project with an AI agent that selects and executes tools to answer user requests. It connects the document question-answering system from Week 9 with the hospital risk prediction service from Week 6.

## Architecture

User request → Agent → Tool selection → Tool execution → Structured response

Available tools:
- `ask_documents` — queries the Week 9 document RAG API.
- `predict_hospital_risk` — calls the Week 6 hospital risk prediction API.
- `lookup_information` — handles supported general information lookups.

Gemini is used for tool selection, with rule-based fallback behaviour when the model call fails.

## Main Components

- `main.py` — FastAPI application and API endpoints.
- `agent.py` — agent orchestration and execution flow.
- `tools.py` — integrations with external project APIs.
- `llm_service.py` — Gemini-based tool selection.
- `schemas.py` — request, response, and tool-call schemas.
- `guardrails.py` — input/tool restrictions and execution limits.
- `tracing.py` — agent execution logging.
- `evaluation.py` — evaluation utilities.
- `evaluation_offline.py` — offline checks for tool selection and guardrails.
- `tests/test_agent.py` — automated agent tests.

## Requirements

Install the dependencies using:

```bash
pip install -r requirements.txt
```

Configure the required Gemini API key in a local `.env` file. Do not commit secrets. `.env.example` should contain placeholder values only.

## Running the API

Start the Week 9 RAG API first if document questions are required:

```bash
cd "../Week 9"
uvicorn main:app --reload --port 8000
```

In a separate terminal, start Week 10:

```bash
cd "../Week 10"
uvicorn main:app --reload --port 8002
```

The Week 10 interactive API documentation is available at:

`http://127.0.0.1:8002/docs`

The Week 10 agent is configured to call Week 9 on port `8000` and Week 6 on port `8001`.

## API Endpoint

### `POST /agent/run`

Example request:

```json
{
  "message": "According to my uploaded document, what are the employee performance appraisal details?"
}
```

The agent selects a suitable tool, executes it, and returns a structured response with execution information and document citations when available.

## Testing

Run the Week 10 test suite:

```bash
python -m pytest tests -v
```

Run the offline evaluation:

```bash
python evaluation_offline.py
```

Latest recorded results during development:
- Automated tests: 19 passed.
- Offline evaluation: 10/10 checks passed.

These results are the last reported results and may change after code updates.

## Guardrails and Limitations

- Tool selection uses Gemini with a rule-based fallback.
- Tool execution is constrained by the available tool definitions and guardrails.
- Document answers rely on the Week 9 RAG service and its retrieved sources.
- Week 6 prediction requests require the Week 6 service to be running.
- Gemini availability may be affected by rate limits or temporary service errors.
- The offline evaluation does not measure live Gemini accuracy or end-to-end answer quality.

## Project Progress

Week 8 introduced document ingestion and vector storage. Week 9 added hybrid retrieval, grounded question answering, citations, and retrieval evaluation. Week 10 integrates these capabilities into a tool-using AI agent alongside the hospital risk prediction service.
