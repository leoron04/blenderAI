# Utility functions for BlenderAI addon

from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable, Iterable


logger = logging.getLogger("blender_ai")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


API_KEY_PATTERN = re.compile(r"^[A-Za-z0-9._-]{12,}$")


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key or len(api_key) < 10:
        return False
    if bool(API_KEY_PATTERN.match(api_key)) is False:
        return False
    return True


def format_response(response: Any, limit: int = 800) -> str:
    """Format AI response for display."""
    if isinstance(response, str):
        return response[:limit]
    return str(response)


def log_message(message: str, level: str = "INFO", secrets: Iterable[str] | None = None) -> None:
    """Log messages for debugging with optional secret redaction."""
    redacted = message
    if secrets:
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "***")
    getattr(logger, level.lower(), logger.info)(redacted)


def safe_execute(func: Callable, *args, **kwargs):
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:  # noqa: BLE001
        log_message(f"Error: {str(e)}", "ERROR")
        return None


def truncate_secret(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return "***"
    return f"{value[:keep]}...{value[-keep:]}"


def pretty_json(data: Any, limit: int = 2000) -> str:
    payload = json.dumps(data, indent=2)
    return payload[:limit]
