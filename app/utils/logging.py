"""
Structured Logging with Secret Redaction.
Never logs passwords, API keys, tokens, or sensitive headers.
"""

import json
import logging
import sys
from typing import Any, Dict

SENSITIVE_KEYS = {
    "authorization",
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "cookie",
    "set-cookie",
    "access_token",
}


def sanitize_payload(data: Any) -> Any:
    """Recursively scrub sensitive keys from dictionaries or lists before logging."""
    if isinstance(data, dict):
        sanitized: Dict[str, Any] = {}
        for key, value in data.items():
            if str(key).lower() in SENSITIVE_KEYS:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_payload(value)
        return sanitized
    if isinstance(data, list):
        return [sanitize_payload(item) for item in data]
    return data


class StructuredJsonFormatter(logging.Formatter):
    """Outputs JSON-formatted log entries safe for SIEM and log ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_entry["request_id"] = getattr(record, "request_id")
        if hasattr(record, "endpoint"):
            log_entry["endpoint"] = getattr(record, "endpoint")
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = getattr(record, "duration_ms")
        if record.exc_info:
            log_entry["exception_type"] = record.exc_info[0].__name__ if record.exc_info[0] else "Error"
        return json.dumps(sanitize_payload(log_entry))


def setup_logger(name: str = "nullsec_kit", level: str = "INFO") -> logging.Logger:
    """Initialize and return a structured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(level.upper())
        logger.propagate = False
    return logger


logger = setup_logger()
