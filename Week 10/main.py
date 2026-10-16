
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from agent import run_agent
from schemas import AgentRequest, AgentResponse
from tracing import trace_event


app = FastAPI(
    title="Week 10 - AI Agent & Tool Use",
    description=(
        "A tool-using agent with guardrails, "
        "structured responses, and execution tracing."
    ),
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "week10-agent",
    }


@app.post("/agent/run", response_model=AgentResponse)
def run_agent_endpoint(request: AgentRequest):
    """Run the agent on a user's message."""
    result = run_agent(request.message)

    trace_event(
        "request_completed",
        {
            "refused": result["refused"],
            "tool_calls": result["tool_calls"],
        },
    )

    return result
