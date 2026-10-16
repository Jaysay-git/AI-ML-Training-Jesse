
import requests


WEEK9_API_URL = "http://127.0.0.1:8000"
WEEK6_API_URL = "http://127.0.0.1:8001"

REQUEST_TIMEOUT = 60


def ask_documents(question: str, n_results: int = 3) -> dict:
    """Ask the Week 9 RAG API a question about uploaded documents."""
    response = requests.post(
        f"{WEEK9_API_URL}/ask",
        json={
            "question": question,
            "n_results": n_results,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def predict_hospital_risk(
    age: int,
    gender: str,
    temperature: float,
    heart_rate: int,
    oxygen_saturation: float,
) -> dict:
    """Request a hospital risk prediction from the Week 6 API."""
    response = requests.post(
        f"{WEEK6_API_URL}/predict",
        json={
            "age": age,
            "gender": gender,
            "temperature": temperature,
            "heart_rate": heart_rate,
            "oxygen_saturation": oxygen_saturation,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def lookup_information(topic: str) -> dict:
    """Provide a controlled lookup for supported course information."""
    supported_topics = {
        "week 6": "Week 6 contains the hospital risk prediction model.",
        "week 9": "Week 9 contains RAG question answering with citations.",
        "week 10": "Week 10 focuses on AI agents, tools, guardrails, tracing, and evaluation.",
        "rag": "RAG retrieves relevant documents to help generate grounded answers.",
        "embedding": "An embedding represents text as a numerical vector.",
        "chroma": "Chroma stores and retrieves vector embeddings for similarity search.",
    }

    normalized_topic = topic.strip().lower()

    if normalized_topic not in supported_topics:
        return {
            "found": False,
            "topic": topic,
            "message": "No information was found for that topic.",
        }

    return {
        "found": True,
        "topic": topic,
        "information": supported_topics[normalized_topic],
    }
