
from unittest.mock import patch

from agent import run_agent
from guardrails import (
    can_call_tool,
    is_allowed_tool,
    is_within_scope,
)
from schemas import ToolCall


def mock_tool_selection(tool_name: str):
    """Mock Gemini selection so unit tests do not call the live API."""
    return patch(
        "agent.choose_tool_with_gemini",
        return_value=ToolCall(
            tool_name=tool_name,
            arguments={},
        ),
    )


def test_rag_request_uses_lookup_tool():
    with mock_tool_selection("lookup_information"):
        result = run_agent("Explain RAG")

    assert result["refused"] is False
    assert result["tool_calls"] == 1
    assert result["steps"][0]["tool_name"] == "lookup_information"
    assert "retrieves relevant documents" in result["answer"]


def test_out_of_scope_request_is_refused():
    result = run_agent("Write me a poem about the ocean")

    assert result["refused"] is True
    assert result["tool_calls"] == 0
    assert result["steps"] == []


def test_unknown_lookup_topic_returns_no_information():
    with mock_tool_selection("lookup_information"):
        result = run_agent("Explain quantum gardening")

    assert result["refused"] is False
    assert result["tool_calls"] == 1
    assert "No information was found" in result["answer"]


def test_unsupported_tool_is_blocked():
    assert is_allowed_tool("delete_database") is False


def test_approved_tool_is_allowed():
    assert is_allowed_tool("ask_documents") is True


def test_tool_call_budget():
    assert can_call_tool(0) is True
    assert can_call_tool(2) is True
    assert can_call_tool(3) is False
    assert can_call_tool(4) is False


def test_rag_is_within_scope():
    assert is_within_scope("Explain RAG") is True


def test_unrelated_request_is_out_of_scope():
    assert is_within_scope("Write me a poem about the ocean") is False


def test_document_api_failure_is_handled():
    with mock_tool_selection("ask_documents"):
        with patch(
            "agent.ask_documents",
            side_effect=ConnectionError("API unavailable"),
        ):
            result = run_agent("Summarize my uploaded hospital report")

    assert result["refused"] is False
    assert result["tool_calls"] == 1
    assert result["steps"][0]["status"] == "failed"
    assert "couldn't complete" in result["answer"]


def test_failed_tool_call_is_traced():
    with mock_tool_selection("ask_documents"):
        with patch(
            "agent.ask_documents",
            side_effect=ConnectionError("API unavailable"),
        ):
            with patch("agent.trace_event") as mock_trace:
                run_agent("Summarize my uploaded hospital report")

    event_names = [
        call.args[0] for call in mock_trace.call_args_list
    ]

    assert "tool_call_started" in event_names
    assert "tool_call_failed" in event_names


def test_empty_request_is_refused():
    result = run_agent("")

    assert result["refused"] is True
    assert result["tool_calls"] == 0
    assert result["steps"] == []


def test_invalid_prediction_input_does_not_call_api():
    with mock_tool_selection("predict_hospital_risk"):
        with patch("agent.predict_hospital_risk") as mock_predict:
            result = run_agent("Predict hospital risk")

    assert result["refused"] is False
    assert result["tool_calls"] == 1
    assert result["steps"][0]["status"] == "failed"
    mock_predict.assert_not_called()

def test_gemini_failure_uses_rule_based_fallback():
    with patch(
        "agent.choose_tool_with_gemini",
        side_effect=RuntimeError("Simulated Gemini failure"),
    ):
        result = run_agent("Explain RAG")

    assert result["refused"] is False
    assert result["tool_calls"] == 1
    assert result["steps"][0]["tool_name"] == "lookup_information"
    assert result["steps"][0]["status"] == "success"
    assert "retrieves relevant documents" in result["answer"]



def test_valid_gemini_topic_is_used():
    selection = ToolCall(
        tool_name="lookup_information",
        arguments={"topic": "week 9"},
    )

    with patch(
        "agent.choose_tool_with_gemini",
        return_value=selection,
    ):
        result = run_agent("Tell me about Week 6")

    assert result["refused"] is False
    assert result["steps"][0]["status"] == "success"
    assert "RAG question answering with citations" in result["answer"]


def test_invalid_gemini_topic_falls_back_to_user_message():
    selection = ToolCall(
        tool_name="lookup_information",
        arguments={"topic": "unsupported topic"},
    )

    with patch(
        "agent.choose_tool_with_gemini",
        return_value=selection,
    ):
        result = run_agent("Explain Week 9")

    assert result["refused"] is False
    assert result["steps"][0]["status"] == "success"
    assert "RAG question answering with citations" in result["answer"]


def test_missing_prediction_measurements_do_not_call_api():
    with mock_tool_selection("predict_hospital_risk"):
        with patch("agent.predict_hospital_risk") as mock_predict:
            result = run_agent("Predict hospital risk")

    assert result["steps"][0]["status"] == "failed"
    mock_predict.assert_not_called()


def test_run_tool_rejects_unregistered_tool():
    from agent import run_tool

    try:
        run_tool("delete_database", "Delete all records")
    except ValueError as exc:
        assert "not allowed or registered" in str(exc)
    else:
        raise AssertionError("An unregistered tool should be rejected.")


def test_appraisal_question_uses_document_fallback():
    from agent import choose_tool

    question = "What are the employee performance appraisal details?"

    assert choose_tool(question) == "ask_documents"


def test_document_citations_are_preserved(monkeypatch):
    from agent import run_agent

    fake_result = {
        "answer": "The appraisal was satisfactory [S1].",
        "citations": [
            {
                "source_id": "S1",
                "filename": "appraisal.pdf",
                "pages": "1",
                "chunk_index": 0,
            }
        ],
    }

    monkeypatch.setattr(
        "agent.select_tool",
        lambda message: ("ask_documents", {}),
    )
    monkeypatch.setattr(
        "agent.run_tool",
        lambda tool_name, message, arguments=None: fake_result,
    )

    response = run_agent(
        "According to my uploaded document, summarize the appraisal."
    )

    assert response["answer"] == "The appraisal was satisfactory [S1]."
    assert response["citations"] == fake_result["citations"]
