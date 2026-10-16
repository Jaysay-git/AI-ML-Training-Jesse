
MAX_TOOL_CALLS = 3

ALLOWED_TOOLS = {
    "ask_documents",
    "predict_hospital_risk",
    "lookup_information",
}

OUT_OF_SCOPE_MESSAGE = (
    "I can help with hospital risk predictions, "
    "questions about uploaded documents, and supported "
    "AI/ML course topics. I can't help with that request."
)


def is_within_scope(message: str) -> bool:
    """Check whether a request relates to a supported capability."""
    text = message.strip().lower()

    if not text:
        return False

    allowed_topics = [
        "hospital",
        "patient",
        "risk",
        "predict",
        "document",
        "report",
        "rag",
        "embedding",
        "chroma",
        "week 6",
        "week 9",
        "week 10",
        "ai",
        "machine learning",
        "model",
        "training",
        "temperature",
        "heart rate",
        "oxygen saturation",
        "symptom",
        "lookup",
    ]

    return any(topic in text for topic in allowed_topics)


def is_allowed_tool(tool_name: str) -> bool:
    """Only allow explicitly registered tools."""
    return tool_name in ALLOWED_TOOLS


def can_call_tool(tool_calls: int) -> bool:
    """Prevent an agent from exceeding its tool-call budget."""
    return 0 <= tool_calls < MAX_TOOL_CALLS
