"""Caching semantico basato su embedding leggeri e profili utente (MVP v0.1)."""

from __future__ import annotations

import json
import math
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

DEFAULT_CACHE_DIR = os.path.expanduser("~/.config/blender_ai/semantic_cache")
PROFILE_PATH = os.path.join(DEFAULT_CACHE_DIR, "preferences.json")


def _ensure_dir(path: str = DEFAULT_CACHE_DIR) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def _hash_tokens(prompt: str, dims: int = 128) -> np.ndarray:
    vec = np.zeros(dims, dtype=np.float32)
    tokens = prompt.lower().split()
    for tok in tokens:
        idx = abs(hash(tok)) % dims
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def _entry_path(cache_dir: str, fingerprint: str, model: str) -> str:
    safe = f"{fingerprint}_{model}".replace("/", "_").replace(":", "_")
    return os.path.join(cache_dir, f"{safe}.json")


def _load_entries(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save_entries(path: str, entries: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def lookup(prompt: str, fingerprint: str, model: str, threshold: float = 0.82) -> Optional[Dict[str, Any]]:
    cache_dir = _ensure_dir()
    path = _entry_path(cache_dir, fingerprint, model)
    entries = _load_entries(path)
    if not entries:
        return None

    query_vec = _hash_tokens(prompt)
    best: Tuple[float, Dict[str, Any]] | None = None
    for entry in entries:
        emb = np.array(entry.get("embedding", []), dtype=np.float32)
        if emb.shape != query_vec.shape:
            continue
        sim = float(np.dot(query_vec, emb))
        if sim >= threshold and (best is None or sim > best[0]):
            best = (sim, entry)
    if best:
        return best[1]
    return None


def store(prompt: str, fingerprint: str, model: str, provider: str, content: str) -> None:
    cache_dir = _ensure_dir()
    path = _entry_path(cache_dir, fingerprint, model)
    entries = _load_entries(path)
    embedding = _hash_tokens(prompt).tolist()
    entries.append(
        {
            "prompt": prompt,
            "fingerprint": fingerprint,
            "model": model,
            "provider": provider,
            "content": content,
            "embedding": embedding,
            "ts": time.time(),
        }
    )
    _save_entries(path, entries[-50:])  # limita dimensione per sicurezza


def _load_profile() -> Dict[str, Any]:
    _ensure_dir()
    if not os.path.exists(PROFILE_PATH):
        return {"providers": {}, "keywords": {}}
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError):
        return {"providers": {}, "keywords": {}}
    return {"providers": {}, "keywords": {}}


def _save_profile(profile: Dict[str, Any]) -> None:
    _ensure_dir()
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def update_preferences(prompt: str, provider: str) -> None:
    profile = _load_profile()
    providers = profile.setdefault("providers", {})
    providers[provider] = providers.get(provider, 0) + 1

    keywords = profile.setdefault("keywords", {})
    for tok in prompt.lower().split():
        keywords[tok] = keywords.get(tok, 0) + 1

    _save_profile(profile)


def top_provider(preferences: Optional[Dict[str, Any]] = None) -> Optional[str]:
    prefs = preferences or _load_profile()
    providers = prefs.get("providers") if isinstance(prefs, dict) else None
    if not providers:
        return None
    return max(providers.items(), key=lambda kv: kv[1])[0]
