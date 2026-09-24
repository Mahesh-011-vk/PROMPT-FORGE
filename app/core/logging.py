"""
PromptForge AI - Structured Logging System.

Provides structured console and JSON logging with contextual metadata
(e.g., request_id, user_id, execution latency).
"""

import json
import logging
import sys
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON for production observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include contextual fields if present
        for field in ("request_id", "user_id", "model", "latency_ms", "tokens"):
            if hasattr(record, field):
                log_payload[field] = getattr(record, field)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
) -> logging.Logger:
    """
    Configures and returns the root application logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_format: If True, outputs JSON records; otherwise, standard formatted text.

    Returns:
        Configured logger instance.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("promptforge")
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers on re-initialization
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        standard_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(standard_formatter)

    logger.addHandler(handler)
    logger.propagate = False
    return logger


# Default logger instance
logger = setup_logging()
