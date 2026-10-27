from llm_service import choose_tool_with_gemini
import json
import re
from typing import Any

from guardrails import (
    ALLOWED_TOOLS,
    OUT_OF_SCOPE_MESSAGE,
    can_call_tool,
    is_within_scope,
)
from schemas import AgentStep, DocumentCitation, HospitalPredictionInput
from tools import (
    ask_documents,
    lookup_information,
    predict_hospital_risk,
)
from tracing import trace_event


TOOL_FUNCTIONS = {
    "ask_documents": ask_documents,
    "lookup_information": lookup_information,
    "predict_hospital_risk": predict_hospital_risk,
}



def choose_tool(message: str) -> str:
    """Choose a tool using simple, transparent fallback rules."""
    text = message.lower()

    # Patient risk predictions take priority.
    if any(word in text for word in [
        "predict", "risk prediction", "oxygen saturation",
        "heart rate", "temperature",
    ]):
        return "predict_hospital_risk"

    # Questions explicitly referring to uploaded documents
    # should be sent to the RAG document-search tool.
    if any(phrase in text for phrase in [
        "uploaded document", "uploaded file", "uploaded pdf",
        "according to the document", "according to my document",
        "appraisal", "employee performance", "document details",
        "in the document", "from the document",
    ]):
        return "ask_documents"

    # Predefined AI/ML concepts and course topics.
    if any(word in text for word in [
        "look up", "lookup", "define", "what is",
        "what are", "explain",
    ]):
        return "lookup_information"

    # Default to document search for other in-scope questions.
    return "ask_documents"


def select_tool(message: str) -> tuple[str, dict[str, Any]]:
    """Select a tool and return its validated arguments."""
    try:
        selection = choose_tool_with_gemini(message)
        tool_name = selection.tool_name
        arguments = selection.arguments

        if tool_name not in ALLOWED_TOOLS or tool_name not in TOOL_FUNCTIONS:
            raise ValueError("Gemini selected an unregistered tool.")

        validated_arguments: dict[str, Any] = {}

        if tool_name == "lookup_information":
            # Only accept known topics; never execute arbitrary arguments.
            topic = arguments.get("topic")

            if isinstance(topic, str):
                normalized_topic = topic.strip().lower()
                supported_topics = {
                    "week 6", "week 9", "week 10",
                    "embedding", "chroma", "rag",
                }

                if normalized_topic in supported_topics:
                    validated_arguments["topic"] = normalized_topic

            trace_event(
                "tool_selection_completed",
                {
                    "method": "gemini",
                    "tool_name": tool_name,
                },
            )
            return tool_name, validated_arguments

        trace_event(
            "tool_selection_completed",
            {
                "method": "gemini",
                "tool_name": tool_name,
            },
        )
        return tool_name, validated_arguments

    except Exception as exc:
        trace_event(
            "tool_selection_fallback",
            {
                "reason": "tool_selection_error",
                "method": "rules",
            },
        )
        return choose_tool(message), {}


def extract_lookup_topic(message: str) -> str:
    """Map a request to a supported lookup topic."""
    text = message.lower()

    for topic in [
        "week 6", "week 9", "week 10",
        "embedding", "chroma", "rag",
    ]:
        if topic in text:
            return topic

    return message.strip()


def extract_prediction_input(message: str) -> dict[str, Any]:
    """Extract and validate patient measurements from JSON in a message."""
    match = re.search(r"\{.*\}", message, re.DOTALL)

    if not match:
        raise ValueError(
            "Include patient measurements as a JSON object with "
            "age, gender, temperature, heart_rate, and oxygen_saturation."
        )

    try:
        data = json.loads(match.group())
        validated = HospitalPredictionInput.model_validate(data)
    except Exception as exc:
        raise ValueError(
            "The patient measurements are missing or invalid. "
            "Check the required fields and their allowed ranges."
        ) from exc

    return validated.model_dump()



def run_tool(
    tool_name: str,
    message: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a tool request and execute the registered function."""
    if tool_name not in ALLOWED_TOOLS or tool_name not in TOOL_FUNCTIONS:
        raise ValueError("This tool is not allowed or registered.")

    arguments = arguments or {}

    if tool_name == "lookup_information":
        topic = arguments.get("topic")

        if not isinstance(topic, str):
            topic = extract_lookup_topic(message)

        return lookup_information(topic)

    if tool_name == "ask_documents":
        return ask_documents(message)

    if tool_name == "predict_hospital_risk":
        # Patient measurements must come from the user's message.
        patient_data = extract_prediction_input(message)
        return predict_hospital_risk(**patient_data)

    raise ValueError("Unsupported tool.")


def run_agent(message: str) -> dict[str, Any]:
    """Process one user request with guardrails and visible steps."""
    message = message.strip()
    steps: list[AgentStep] = []
    tool_calls = 0

    trace_event("request_started", {"message_length": len(message)})

    if not is_within_scope(message):
        trace_event("request_refused", {"reason": "out_of_scope"})
        return {
            "message": message,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "steps": [],
            "tool_calls": 0,
            "refused": True,
        }

    tool_name, tool_arguments = select_tool(message)

    if not can_call_tool(tool_calls):
        return {
            "message": message,
            "answer": "The maximum number of tool calls has been reached.",
            "steps": [],
            "tool_calls": tool_calls,
            "refused": False,
        }

    tool_calls += 1
    trace_event(
        "tool_call_started",
        {"tool_name": tool_name, "tool_call_number": tool_calls},
    )

    try:
        result = run_tool(tool_name, message, tool_arguments)
        citations = []

        if tool_name == "ask_documents":
            citations = result.get("citations", [])

        steps.append(
            AgentStep(
                step=1,
                tool_name=tool_name,
                status="success",
                details=f"{tool_name} completed successfully.",
            )
        )

        trace_event(
            "tool_call_completed",
            {"tool_name": tool_name, "status": "success"},
        )

        if tool_name == "ask_documents":
            answer = result.get("answer", str(result))
        elif tool_name == "lookup_information":
            answer = result.get(
                "information",
                result.get("message", "No information was found."),
            )
        else:
            answer = (
                "Hospital risk prediction result: "
                + json.dumps(result, ensure_ascii=False, default=str)
                + ". This model output is not a medical diagnosis."
            )

        return {
            "message": message,
            "answer": answer,
            "steps": [step.model_dump() for step in steps],
            "tool_calls": tool_calls,
            "refused": False,
            "citations": [
                DocumentCitation.model_validate(citation).model_dump()
                for citation in citations
            ],
}

    except Exception as exc:
        trace_event(
            "tool_call_failed",
            {
                "tool_name": tool_name,
                "error": "tool_execution_error",
            },
        )

        steps.append(
            AgentStep(
                step=1,
                tool_name=tool_name,
                status="failed",
                details="The tool failed. Check the agent logs.",
            )
        )

        return {
            "message": message,
            "answer": (
                "I couldn't complete that request. "
                "Check the input measurements and confirm the required API is running."
            ),
            "steps": [step.model_dump() for step in steps],
            "tool_calls": tool_calls,
            "refused": False,
        }
