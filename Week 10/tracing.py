
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "agent.jsonl"

logger = logging.getLogger("week10_agent")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def trace_event(
    event: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a structured event in the agent log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "details": details or {},
    }

    logger.info(json.dumps(record, ensure_ascii=False, default=str))
    return record
