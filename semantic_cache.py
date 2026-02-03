"""Semantic caching with TF-IDF embeddings and user preference learning.

This module provides intelligent caching that:
- Uses TF-IDF vectorization for semantic similarity matching
- Supports n-gram features for better phrase matching
- Filters stopwords for more meaningful comparisons
- Learns user preferences over time
- Expires old cache entries automatically
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

DEFAULT_CACHE_DIR = os.path.expanduser("~/.config/blender_ai/semantic_cache")
PROFILE_PATH = os.path.join(DEFAULT_CACHE_DIR, "preferences.json")
IDF_PATH = os.path.join(DEFAULT_CACHE_DIR, "idf_index.json")

# Cache entry expiration (7 days)
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60

# Common English stopwords for filtering
STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "this", "that",
    "these", "those", "i", "you", "he", "she", "it", "we", "they", "what",
    "which", "who", "whom", "where", "when", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "also", "now", "here", "there", "then", "once", "if", "any", "me", "my",
    "per", "il", "la", "le", "lo", "un", "una", "e", "che", "di", "da",
    "con", "su", "per", "tra", "fra", "come", "dove", "quando", "perche",
}


def _ensure_dir(path: str = DEFAULT_CACHE_DIR) -> str:
    """Ensure cache directory exists."""
    os.makedirs(path, exist_ok=True)
    return path


def _tokenize(text: str) -> List[str]:
    """Tokenize text into words, removing punctuation and stopwords."""
    # Lowercase and split on non-alphanumeric
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    # Filter stopwords and very short tokens
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _get_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Generate n-grams from token list."""
    if len(tokens) < n:
        return []
    return ['_'.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def _extract_features(text: str) -> List[str]:
    """Extract unigrams and bigrams as features."""
    tokens = _tokenize(text)
    bigrams = _get_ngrams(tokens, 2)
    return tokens + bigrams


def _load_idf_index() -> Dict[str, float]:
    """Load IDF index from disk."""
    _ensure_dir()
    if not os.path.exists(IDF_PATH):
        return {}
    try:
        with open(IDF_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_idf_index(idf: Dict[str, float]) -> None:
    """Save IDF index to disk."""
    _ensure_dir()
    with open(IDF_PATH, "w", encoding="utf-8") as f:
        json.dump(idf, f)


def _update_idf(features: List[str], doc_count: int = 1) -> Dict[str, float]:
    """Update IDF index with new document features."""
    idf = _load_idf_index()

    # Track document count
    total_docs = idf.get("__total_docs__", 0) + doc_count
    idf["__total_docs__"] = total_docs

    # Update document frequency for each unique feature
    unique_features = set(features)
    for feature in unique_features:
        df_key = f"__df__{feature}"
        idf[df_key] = idf.get(df_key, 0) + 1

    # Recalculate IDF values
    for key in list(idf.keys()):
        if key.startswith("__df__"):
            feature = key[6:]  # Remove __df__ prefix
            df = idf[key]
            # IDF = log(N / df) + 1 (smoothed)
            idf[feature] = math.log(total_docs / max(df, 1)) + 1

    _save_idf_index(idf)
    return idf


def _compute_tfidf_vector(features: List[str], idf: Dict[str, float], dims: int = 256) -> np.ndarray:
    """Compute TF-IDF vector for given features.

    Uses feature hashing to map to fixed dimensions, weighted by TF-IDF.
    """
    vec = np.zeros(dims, dtype=np.float32)

    # Compute term frequencies
    tf = Counter(features)
    total = len(features) if features else 1

    for feature, count in tf.items():
        # TF: normalized term frequency
        term_freq = count / total

        # IDF: from index or default
        inv_doc_freq = idf.get(feature, 1.0)

        # TF-IDF weight
        weight = term_freq * inv_doc_freq

        # Hash to dimension
        idx = abs(hash(feature)) % dims
        vec[idx] += weight

    # L2 normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm

    return vec


def _cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    if v1.shape != v2.shape:
        return 0.0
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


def _entry_path(cache_dir: str, fingerprint: str, model: str) -> str:
    """Get cache file path for given fingerprint and model."""
    safe = f"{fingerprint}_{model}".replace("/", "_").replace(":", "_")
    return os.path.join(cache_dir, f"{safe}.json")


def _load_entries(path: str) -> List[Dict[str, Any]]:
    """Load cache entries from file."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save_entries(path: str, entries: List[Dict[str, Any]]) -> None:
    """Save cache entries to file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def _filter_expired(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove expired cache entries."""
    now = time.time()
    return [e for e in entries if now - e.get("ts", 0) < CACHE_TTL_SECONDS]


def lookup(
    prompt: str,
    fingerprint: str,
    model: str,
    threshold: float = 0.82
) -> Optional[Dict[str, Any]]:
    """Look up cached response with semantic similarity matching.

    Args:
        prompt: User query to match
        fingerprint: Scene fingerprint
        model: AI model identifier
        threshold: Minimum similarity score (0-1)

    Returns:
        Cached entry dict or None if no match above threshold
    """
    cache_dir = _ensure_dir()
    path = _entry_path(cache_dir, fingerprint, model)
    entries = _load_entries(path)

    if not entries:
        return None

    # Filter expired entries
    entries = _filter_expired(entries)
    if not entries:
        return None

    # Extract features and compute query vector
    query_features = _extract_features(prompt)
    idf = _load_idf_index()
    query_vec = _compute_tfidf_vector(query_features, idf)

    # Find best match
    best_match: Optional[Tuple[float, Dict[str, Any]]] = None

    for entry in entries:
        emb = entry.get("embedding")
        if not emb:
            continue

        entry_vec = np.array(emb, dtype=np.float32)
        if entry_vec.shape != query_vec.shape:
            continue

        similarity = _cosine_similarity(query_vec, entry_vec)

        if similarity >= threshold:
            if best_match is None or similarity > best_match[0]:
                best_match = (similarity, entry)

    if best_match:
        return best_match[1]

    return None


def store(
    prompt: str,
    fingerprint: str,
    model: str,
    provider: str,
    content: str
) -> None:
    """Store response in semantic cache.

    Args:
        prompt: User query
        fingerprint: Scene fingerprint
        model: AI model identifier
        provider: AI provider name
        content: Response content to cache
    """
    cache_dir = _ensure_dir()
    path = _entry_path(cache_dir, fingerprint, model)
    entries = _load_entries(path)

    # Filter expired entries
    entries = _filter_expired(entries)

    # Extract features and update IDF
    features = _extract_features(prompt)
    idf = _update_idf(features)

    # Compute embedding
    embedding = _compute_tfidf_vector(features, idf).tolist()

    # Create entry
    entry = {
        "prompt": prompt,
        "fingerprint": fingerprint,
        "model": model,
        "provider": provider,
        "content": content,
        "embedding": embedding,
        "features": features[:50],  # Store top features for debugging
        "ts": time.time(),
    }

    entries.append(entry)

    # Limit cache size (keep most recent 100 entries)
    _save_entries(path, entries[-100:])


def _load_profile() -> Dict[str, Any]:
    """Load user preference profile."""
    _ensure_dir()
    if not os.path.exists(PROFILE_PATH):
        return {"providers": {}, "keywords": {}, "topics": {}}
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"providers": {}, "keywords": {}, "topics": {}}


def _save_profile(profile: Dict[str, Any]) -> None:
    """Save user preference profile."""
    _ensure_dir()
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def update_preferences(prompt: str, provider: str) -> None:
    """Update user preferences based on interaction.

    Tracks:
    - Provider usage frequency
    - Keyword frequency for topic modeling
    - Topic categories based on keywords
    """
    profile = _load_profile()

    # Update provider preference
    providers = profile.setdefault("providers", {})
    providers[provider] = providers.get(provider, 0) + 1

    # Update keyword preferences
    keywords = profile.setdefault("keywords", {})
    features = _extract_features(prompt)
    for feature in features:
        keywords[feature] = keywords.get(feature, 0) + 1

    # Detect and track topics
    topics = profile.setdefault("topics", {})
    topic_keywords = {
        "materials": {"material", "shader", "texture", "pbr", "metallic", "roughness"},
        "lighting": {"light", "lamp", "sun", "spot", "area", "shadow", "illumination"},
        "animation": {"animation", "keyframe", "frame", "motion", "animate", "rig"},
        "modeling": {"mesh", "vertex", "edge", "face", "polygon", "geometry", "model"},
        "rendering": {"render", "cycles", "eevee", "sample", "denoise", "output"},
        "rigging": {"rig", "bone", "armature", "weight", "pose", "skeleton"},
    }

    for topic, topic_words in topic_keywords.items():
        if any(f in topic_words for f in features):
            topics[topic] = topics.get(topic, 0) + 1

    _save_profile(profile)


def top_provider(preferences: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Get user's most frequently used provider."""
    prefs = preferences or _load_profile()
    providers = prefs.get("providers") if isinstance(prefs, dict) else None
    if not providers:
        return None
    return max(providers.items(), key=lambda kv: kv[1])[0]


def get_user_topics() -> List[Tuple[str, int]]:
    """Get user's top topics sorted by frequency."""
    profile = _load_profile()
    topics = profile.get("topics", {})
    return sorted(topics.items(), key=lambda kv: kv[1], reverse=True)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for debugging/monitoring."""
    cache_dir = _ensure_dir()

    total_entries = 0
    total_files = 0
    oldest_entry = None
    newest_entry = None

    for filename in os.listdir(cache_dir):
        if filename.endswith(".json") and not filename.startswith("preferences") and not filename.startswith("idf"):
            total_files += 1
            entries = _load_entries(os.path.join(cache_dir, filename))
            total_entries += len(entries)

            for entry in entries:
                ts = entry.get("ts", 0)
                if oldest_entry is None or ts < oldest_entry:
                    oldest_entry = ts
                if newest_entry is None or ts > newest_entry:
                    newest_entry = ts

    idf = _load_idf_index()
    vocab_size = sum(1 for k in idf.keys() if not k.startswith("__"))

    return {
        "total_entries": total_entries,
        "total_files": total_files,
        "vocabulary_size": vocab_size,
        "oldest_entry_age_hours": (time.time() - oldest_entry) / 3600 if oldest_entry else None,
        "newest_entry_age_hours": (time.time() - newest_entry) / 3600 if newest_entry else None,
    }
