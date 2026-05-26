"""Caching locale per prompt/risposte e analisi scena."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional, Tuple

from . import utils
DEFAULT_CACHE_DIR = utils.get_config_dir("cache")


def ensure_cache_dir(path: str = DEFAULT_CACHE_DIR) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except OSError:
        fallback = os.path.join(os.path.dirname(__file__), "cache")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def _cache_path(key: str, cache_dir: str) -> str:
    safe_key = key.replace("/", "_").replace(":", "_")
    return os.path.join(cache_dir, f"{safe_key}.json")


def load_cache(key: str, cache_dir: str = DEFAULT_CACHE_DIR) -> Optional[Dict[str, Any]]:
    cache_dir = ensure_cache_dir(cache_dir)
    path = _cache_path(key, cache_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def save_cache(key: str, data: Dict[str, Any], cache_dir: str = DEFAULT_CACHE_DIR) -> str:
    cache_dir = ensure_cache_dir(cache_dir)
    payload = {"data": data, "ts": time.time()}
    path = _cache_path(key, cache_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def cache_key(prompt: str, scene_fingerprint: str, model: str) -> str:
    return f"{model}_{scene_fingerprint}_{abs(hash(prompt))}"

