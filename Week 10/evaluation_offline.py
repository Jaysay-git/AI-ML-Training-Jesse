
import json

from agent import choose_tool
from guardrails import is_within_scope


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
        "name": "Football joke",
        "message": "Tell me a joke about football",
        "expected_tool": None,
        "expected_refusal": True,
    },
]


def evaluate_offline() -> dict:
    """Evaluate rule-based selection and scope guardrails."""
    results = []

    for case in EVALUATION_CASES:
        message = case["message"]
        within_scope = is_within_scope(message)

        if within_scope:
            actual_tool = choose_tool(message)
            actual_refusal = False
        else:
            actual_tool = None
            actual_refusal = True

        tool_correct = actual_tool == case["expected_tool"]
        refusal_correct = (
            actual_refusal == case["expected_refusal"]
        )

        results.append({
            "name": case["name"],
            "expected_tool": case["expected_tool"],
            "actual_tool": actual_tool,
            "tool_correct": tool_correct,
            "expected_refusal": case["expected_refusal"],
            "actual_refusal": actual_refusal,
            "refusal_correct": refusal_correct,
            "passed": tool_correct and refusal_correct,
        })

    passed = sum(item["passed"] for item in results)
    total = len(results)

    return {
        "evaluation_type": "Offline rule-based selection and guardrails",
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(passed / total, 4) if total else 0.0,
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_offline(), indent=2))
