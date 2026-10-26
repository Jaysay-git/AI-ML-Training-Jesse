# Week 10 — AI Agent Integration

## Overview

Week 10 extends the hospital AI/ML course project with an AI agent that selects and executes tools to answer user requests. It connects the document question-answering system from Week 9 with the hospital risk prediction service from Week 6.

## Architecture

**User request → Agent → Tool selection → Tool execution → Structured response**

### Available tools

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

## Requirements and Configuration

Run the commands below from the repository's `Week 10` directory, using the course virtual environment if it is already configured.

```powershell
Set-Location "C:\Users\jesseos\Downloads\AI-ML COURSE\Week 10"
& "..\Week 8\jaysay\Scripts\Activate.ps1"
python -m pip install -r requirements.txt
```

Configure the required Gemini API key in a local `.env` file if needed by your configuration. Never commit real API keys or other secrets. The `.env.example` file should contain placeholder values only.

## Running the APIs

### 1. Start the Week 9 RAG API

Open a terminal:

```powershell
Set-Location "C:\Users\jesseos\Downloads\AI-ML COURSE\Week 9"
& "..\Week 8\jaysay\Scripts\Activate.ps1"
python -m uvicorn main:app --reload --port 8000
```

Week 9 must be running for document question-answering requests. Ensure the relevant documents have been ingested into the RAG system.

### 2. Start the Week 6 prediction API

In another terminal, start the Week 6 application using its configured entry point and port `8001`.

The Week 6 service must be running for hospital-risk prediction requests. Confirm its actual startup command in the Week 6 README or application configuration.

### 3. Start the Week 10 agent

Open another terminal:

```powershell
Set-Location "C:\Users\jesseos\Downloads\AI-ML COURSE\Week 10"
& "..\Week 8\jaysay\Scripts\Activate.ps1"
python -m uvicorn main:app --reload --port 8002
```

The Week 10 interactive API documentation is available at:

**http://127.0.0.1:8002/docs**

The agent calls Week 9 on port `8000` and Week 6 on port `8001`.

## API Endpoint

### `POST /agent/run`

Example request:

```json
{
  "message": "According to my uploaded document, what are the employee performance appraisal details?"
}
```

The agent selects a suitable tool, executes it, and returns a structured response containing the answer and execution information, with document citations when available.

Use the interactive Swagger documentation at `/docs` to submit requests and inspect responses.

## Viewing Agent Logs

After submitting at least one request to the agent, open a terminal in the Week 10 directory and run:

```powershell
Get-Content .\logs\agent.jsonl -Tail 20
```

This displays the latest entries in the agent log, if logging has created the file.

The logs can help inspect tool execution and errors. The exact event details depend on the tracing implementation.

## Testing

From the Week 10 directory, run the automated tests:

```powershell
python -m pytest tests -v
```

Run the offline evaluation:

```powershell
python evaluation_offline.py
```

These commands test the local agent implementation and the offline evaluation scenarios. They do not, by themselves, prove that Gemini or the Week 6 and Week 9 APIs are working end to end.

### Previously Recorded Results

- Automated tests: 19 passed.
- Offline evaluation: 10/10 checks passed.

These are historical development results. Run the commands above to verify the current code.

## Guardrails and Limitations

- Tool selection uses Gemini with a rule-based fallback.
- Tool execution is constrained by the available tool definitions and guardrails.
- Document answers depend on the Week 9 RAG service and its retrieved sources.
- Week 6 prediction requests require the Week 6 service to be running.
- Gemini availability may be affected by rate limits or temporary service errors.
- The offline evaluation does not measure live Gemini accuracy or end-to-end answer quality.

## Project Progress

Week 8 introduced document ingestion and vector storage. Week 9 added hybrid retrieval, grounded question answering, citations, and retrieval evaluation. Week 10 integrates these capabilities into a tool-using AI agent alongside the hospital risk prediction service.
