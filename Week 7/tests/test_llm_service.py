import logging
from unittest.mock import Mock, patch

import pytest
from google.genai.errors import ServerError

from llm_service import (
    ESTIMATED_COST_PER_REQUEST,
    MalformedLLMResponseError,
    extract_patient_information,
)
from schemas import ExtractedPatientInfo


def mock_gemini_response():
    response = Mock()
    response.text = """
    {
        "name": "John Doe",
        "age": 45,
        "gender": "male",
        "symptoms": ["fever", "headache"],
        "temperature": 38.5
    }
    """
    return response


def test_structured_patient_extraction():
    """Verify Gemini output is parsed into the expected Pydantic schema."""

    with patch(
        "llm_service.client.models.generate_content"
    ) as mock_generate:
        mock_generate.return_value = mock_gemini_response()

        result = extract_patient_information(
            "John Doe is 45 years old, male, with fever and headache. "
            "His temperature is 38.5°C."
        )

    assert isinstance(result, ExtractedPatientInfo)
    assert result.name == "John Doe"
    assert result.age == 45
    assert result.gender == "male"
    assert result.symptoms == ["fever", "headache"]
    assert result.temperature == 38.5


def test_cost_and_latency_are_logged(caplog):
    """Verify every successful LLM call records cost and latency."""

    with patch(
        "llm_service.client.models.generate_content"
    ) as mock_generate:
        mock_generate.return_value = mock_gemini_response()

        with caplog.at_level(
            logging.INFO,
            logger="hospital_llm"
        ):
            extract_patient_information(
                "John Doe is 45 years old and has a temperature of 38.5°C."
            )

    log_output = caplog.text

    assert "llm_request_success" in log_output
    assert "latency=" in log_output
    assert "estimated_cost=" in log_output
    assert "estimated_cost_per_100=" in log_output
    assert f"{ESTIMATED_COST_PER_REQUEST:.6f}" in log_output


def test_retry_after_temporary_gemini_failure():
    """Verify the service retries once after a temporary Gemini failure."""

    temporary_error = ServerError(
        503,
        {"error": {"message": "Temporary Gemini failure"}}
    )

    with patch(
        "llm_service.client.models.generate_content"
    ) as mock_generate:
        mock_generate.side_effect = [
            temporary_error,
            mock_gemini_response(),
        ]

        result = extract_patient_information(
            "John Doe is 45 years old."
        )

    assert mock_generate.call_count == 2
    assert isinstance(result, ExtractedPatientInfo)


def test_malformed_response_raises_error():
    """Verify invalid structured output is rejected."""

    malformed_response = Mock()
    malformed_response.text = """
    {
        "name": 123,
        "age": "not-a-number"
    }
    """

    with patch(
        "llm_service.client.models.generate_content"
    ) as mock_generate:
        mock_generate.return_value = malformed_response

        with pytest.raises(MalformedLLMResponseError):
            extract_patient_information(
                "John Doe is 45 years old."
            )
