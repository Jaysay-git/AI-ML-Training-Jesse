import logging
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

from schemas import ExtractedPatientInfo


load_dotenv()

logger = logging.getLogger("hospital_llm")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


SYSTEM_PROMPT = """
You are a patient information extraction assistant.

Extract information that is explicitly provided in the user's text.

Your job is to identify information that can help the application
find an existing patient in its database and identify any new
information mentioned about that patient.

Extract:
- name
- age
- gender
- symptoms
- temperature

Only extract information that is explicitly provided.

Do not guess, invent, or create patient IDs, email addresses,
phone numbers, or other database information.

The application will retrieve the patient's existing record
from its database separately.
"""


# Application-level cost estimate for monitoring.
ESTIMATED_COST_PER_REQUEST = 0.001


class MalformedLLMResponseError(ValueError):
    """Raised when Gemini returns invalid structured data."""
    pass


def extract_patient_information(
    text: str,
) -> ExtractedPatientInfo:

    max_attempts = 2

    for attempt in range(1, max_attempts + 1):

        start_time = time.perf_counter()

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=f"{SYSTEM_PROMPT}\n\nPatient text:\n{text}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ExtractedPatientInfo,
                    "http_options": {
                        "timeout": 10000
                    },
                },
            )

            latency = time.perf_counter() - start_time

            logger.info(
                "llm_request_success "
                "attempt=%s latency=%.4fs "
                "estimated_cost=$%.6f "
                "estimated_cost_per_100=$%.4f",
                attempt,
                latency,
                ESTIMATED_COST_PER_REQUEST,
                ESTIMATED_COST_PER_REQUEST * 100,
            )

            response_text = response.text

            try:
                return ExtractedPatientInfo.model_validate_json(
                    response_text
                )

            except Exception as exc:
                logger.error(
                    "llm_malformed_response error=%s",
                    str(exc),
                )

                raise MalformedLLMResponseError(
                    "Gemini returned an invalid structured response."
                ) from exc

        except MalformedLLMResponseError:
            raise

        except ServerError as exc:

            latency = time.perf_counter() - start_time

            logger.warning(
                "llm_request_failed "
                "attempt=%s latency=%.4fs error=%s",
                attempt,
                latency,
                str(exc),
            )

            if attempt < max_attempts:
                logger.info(
                    "Temporary Gemini failure. Retrying once..."
                )
                continue

            raise RuntimeError(
                "Gemini is temporarily unavailable after one retry."
            ) from exc

        except TimeoutError as exc:

            latency = time.perf_counter() - start_time

            logger.warning(
                "llm_request_timeout "
                "attempt=%s latency=%.4fs",
                attempt,
                latency,
            )

            if attempt < max_attempts:
                logger.info(
                    "Gemini request timed out. Retrying once..."
                )
                continue

            raise RuntimeError(
                "Gemini request timed out after one retry."
            ) from exc

        except Exception as exc:

            latency = time.perf_counter() - start_time
            error_message = str(exc)

            # Gemini's SDK may raise a generic exception for timeouts.
            if "timed out" in error_message.lower():

                logger.warning(
                    "llm_request_timeout "
                    "attempt=%s latency=%.4fs",
                    attempt,
                    latency,
                )

                if attempt < max_attempts:
                    logger.info(
                        "Gemini request timed out. Retrying once..."
                    )
                    continue

                raise RuntimeError(
                    "Gemini request timed out after one retry."
                ) from exc

            logger.error(
                "llm_request_error "
                "attempt=%s latency=%.4fs error=%s",
                attempt,
                latency,
                error_message,
            )

            raise RuntimeError(
                "An unexpected error occurred while processing the LLM request."
            ) from exc