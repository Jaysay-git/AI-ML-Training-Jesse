import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from agent import run_agent
from monitoring import configure_monitoring
from schemas import AgentRequest, AgentResponse
from tracing import trace_event


load_dotenv()
configure_monitoring()


app = FastAPI(
    title="Week 10 - AI Agent & Tool Use",
    description=(
        "A tool-using agent with guardrails, "
        "structured responses, and execution tracing."
    ),
    version="1.0.0",
)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Record HTTP status and duration without logging request contents."""
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        trace_event(
            "http_request",
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(
                    (time.perf_counter() - start_time) * 1000, 2
                ),
            },
        )

        return response

    except Exception:
        trace_event(
            "http_request_failed",
            {
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(
                    (time.perf_counter() - start_time) * 1000, 2
                ),
            },
        )
        raise


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
