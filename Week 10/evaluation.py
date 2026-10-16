
import json

from dotenv import load_dotenv

from guardrails import is_within_scope
from llm_service import choose_tool_with_gemini


load_dotenv()


EVALUATION_CASES = [
    {
        "name": "RAG explanation",
        "message": "Explain RAG",
        "expected_tool": "lookup_information",
        "expected_refusal": False,
    },
    {
        "name": "Embedding explanation",
        "message": "Explain embedding",
        "expected_tool": "lookup_information",
        "expected_refusal": False,
    },
    {
        "name": "Hospital risk prediction",
        "message": (
            "Predict hospital risk using these measurements: "
            '{"age": 45, "gender": "male", "temperature": 37.0, '
            '"heart_rate": 80, "oxygen_saturation": 98.0}'
        ),
        "expected_tool": "predict_hospital_risk",
        "expected_refusal": False,
    },
    {
        "name": "Document question",
        "message": "Summarize my uploaded hospital report",
        "expected_tool": "ask_documents",
        "expected_refusal": False,
    },
    {
        "name": "Out-of-scope request",
        "message": "Write me a poem about the ocean",
        "expected_tool": None,
        "expected_refusal": True,
    },
    {
        "name": "Unknown lookup topic",
        "message": "Explain quantum gardening",
        "expected_tool": "lookup_information",
        "expected_refusal": False,
    },
    {
        "name": "Chroma explanation",
        "message": "What is Chroma?",
        "expected_tool": "lookup_information",
        "expected_refusal": False,
    },
    {
        "name": "Week 9 explanation",
        "message": "Explain Week 9",
        "expected_tool": "lookup_information",
        "expected_refusal": False,
    },
    {
        "name": "Heart rate risk prediction",
        "message": (
            "Predict risk for patient with heart rate 95, "
            "temperature 37.2, and oxygen saturation 96"
        ),
        "expected_tool": "predict_hospital_risk",
        "expected_refusal": False,
    },
    {
        "name": "Another unrelated request",
        "message": "Tell me a joke about football",
        "expected_tool": None,
        "expected_refusal": True,
    },
]


def evaluate_agent() -> dict:
    """Evaluate live Gemini tool selection and refusal guardrails."""
    results = []

    for case in EVALUATION_CASES:
        message = case["message"]
        expected_tool = case["expected_tool"]
        expected_refusal = case["expected_refusal"]

        if not is_within_scope(message):
            actual_tool = None
            actual_refusal = True
            error = None
        else:
            actual_refusal = False
            error = None

            try:
                selection = choose_tool_with_gemini(message)
                actual_tool = selection.tool_name
            except Exception as exc:
                actual_tool = None
                error = f"{type(exc).__name__}: {exc}"

        tool_correct = actual_tool == expected_tool
        refusal_correct = actual_refusal == expected_refusal

        results.append(
            {
                "name": case["name"],
                "expected_tool": expected_tool,
                "actual_tool": actual_tool,
                "tool_correct": tool_correct,
                "expected_refusal": expected_refusal,
                "actual_refusal": actual_refusal,
                "refusal_correct": refusal_correct,
                "error": error,
                "passed": (
                    tool_correct
                    and refusal_correct
                    and error is None
                ),
            }
        )

    passed = sum(item["passed"] for item in results)
    total = len(results)

    return {
        "evaluation_type": "Live Gemini tool selection and guardrails",
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(passed / total, 4) if total else 0.0,
        "results": results,
    }


if __name__ == "__main__":
    report = evaluate_agent()
    print(json.dumps(report, indent=2))
