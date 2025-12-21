from __future__ import annotations

"""Security utilities and decorators for BlenderAI."""

import logging
import os
import re
import time
from collections import defaultdict, deque
from typing import Any, Dict, Iterable, Mapping, Tuple

from . import utils

logger = logging.getLogger("blender_ai.security")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[SECURITY] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B-\x1F\x7F]")
SENSITIVE_KEYS = {"openai_key", "anthropic_key", "google_key", "api_key", "authorization"}


def sanitize_text(text: str | None, max_length: int = 4096) -> str:
    """Strip control chars and hard-limit length."""
    if text is None:
        return ""
    cleaned = CONTROL_CHARS.sub("", str(text))
    return cleaned.strip()[:max_length]


def sanitize_user_input(value: str | None, field_name: str, max_length: int = 512, allow_empty: bool = False) -> str:
    cleaned = sanitize_text(value, max_length=max_length)
    if not allow_empty and not cleaned:
        raise ValueError(f"{field_name} non può essere vuoto.")
    return cleaned


def validate_port(port: int, field_name: str = "port") -> int:
    if not isinstance(port, int):
        raise ValueError(f"{field_name} deve essere un intero.")
    if port < 1 or port > 65535:
        raise ValueError(f"{field_name} deve essere tra 1 e 65535.")
    return port


def mask_secret(secret: str | None, keep: int = 3) -> str:
    if not secret:
        return ""
    if len(secret) <= keep * 2:
        return "***"
    return f"{secret[:keep]}...{secret[-keep:]}"


def redact_secrets(message: str, secrets: Iterable[str]) -> str:
    redacted = message
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "***")
            redacted = redacted.replace(mask_secret(secret), "***")
    return redacted


def redact_config(config: Mapping[str, Any], sensitive_keys: Iterable[str] | None = None) -> Dict[str, Any]:
    sensitive_keys = set(sensitive_keys or SENSITIVE_KEYS)
    return {k: ("***" if k in sensitive_keys else v) for k, v in config.items()}


def validate_environment(env: Mapping[str, str] | None = None) -> Tuple[Dict[str, str], list[str]]:
    env = env or os.environ
    validated: Dict[str, str] = {}
    errors: list[str] = []
    mapping = {
        "OPENAI_API_KEY": "openai_api_key",
        "ANTHROPIC_API_KEY": "anthropic_api_key",
        "GOOGLE_API_KEY": "google_api_key",
    }

    for env_key, target in mapping.items():
        value = env.get(env_key, "")
        if not value:
            continue
        if not utils.validate_api_key(value):
            errors.append(f"{env_key} non valida: formato errato.")
            continue
        validated[target] = value
    return validated, errors


class SlidingRateLimiter:
    """Per-provider sliding window rate limiter."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = max(limit, 1)
        self.window_seconds = max(window_seconds, 1)
        self._events: Dict[str, deque[float]] = defaultdict(deque)

    def allow(self, bucket: str) -> bool:
        now = time.time()
        events = self._events[bucket]
        while events and now - events[0] > self.window_seconds:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(now)
        return True


_LIMITERS: Dict[str, SlidingRateLimiter] = {}


def enforce_rate_limit(bucket: str, limit: int, window_seconds: int, identifier: str | None = None) -> None:
    limiter = _LIMITERS.setdefault(bucket, SlidingRateLimiter(limit=limit, window_seconds=window_seconds))
    key = identifier or bucket
    if not limiter.allow(key):
        raise RuntimeError(f"Rate limit superato per {key} ({limit} richieste ogni {window_seconds}s).")


def ensure_safe_message(message: str, secrets: Iterable[str]) -> str:
    return sanitize_text(redact_secrets(message, secrets))
