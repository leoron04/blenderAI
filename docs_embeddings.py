"""Embedding e indicizzazione per la documentazione Blender."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

try:
    from .blender_docs_manager import DocEntry, default_manager
    from . import utils
except ImportError:  # pragma: no cover - fallback execution path
    from blender_docs_manager import DocEntry, default_manager  # type: ignore
    import utils  # type: ignore

try:
    import openai
except Exception:  # noqa: BLE001
    openai = None  # type: ignore


EMBED_DIM = 384


def _hash_vector(text: str, dim: int = EMBED_DIM) -> np.ndarray:
    """Embedding deterministico fallback."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    return rng.standard_normal(dim)


def _openai_embed(text: str, model: str = "text-embedding-3-small") -> np.ndarray:
    if not openai or not os.getenv("OPENAI_API_KEY"):
        return _hash_vector(text)
    client = openai.OpenAI()
    response = client.embeddings.create(model=model, input=text[:8000])
    return np.array(response.data[0].embedding, dtype=np.float32)


def chunk_entry(entry: DocEntry, max_chunk: int = 600) -> List[Tuple[str, Dict]]:
    """Crea chunk semantici preservando la gerarchia."""
    base_meta = {
        "version": entry.version,
        "category": entry.category,
        "type": entry.type,
        "name": entry.name,
        "path": entry.path,
    }
    payloads: List[Tuple[str, Dict]] = []
    parts = [entry.docstring] + entry.examples
    text = "\n\n".join(parts)
    if len(text) <= max_chunk:
        payloads.append((text, base_meta))
        return payloads
    for idx, chunk_start in enumerate(range(0, len(text), max_chunk)):
        payloads.append((text[chunk_start : chunk_start + max_chunk], {**base_meta, "chunk": idx}))
    return payloads


@dataclass
class EmbeddingRecord:
    embedding: np.ndarray
    metadata: Dict
    text: str


class DocsEmbeddingIndex:
    def __init__(self, storage_dir: str | Path = "data/blender_docs", embed_model: str = "text-embedding-3-small"):
        self.storage_dir = Path(storage_dir)
        self.embed_model = embed_model
        self.embeddings_dir = self.storage_dir / "embeddings"
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        self.manager = default_manager()
        self.records: List[EmbeddingRecord] = []

    def build(self, versions: Iterable[str]) -> None:
        self.records = []
        for version in versions:
            entries = self.manager.load_entries(version)
            self.records.extend(self._embed_entries(entries))
        self._persist()

    def _embed_entries(self, entries: List[DocEntry]) -> List[EmbeddingRecord]:
        records: List[EmbeddingRecord] = []
        for entry in entries:
            for chunk, meta in chunk_entry(entry):
                vector = _openai_embed(chunk, model=self.embed_model)
                records.append(EmbeddingRecord(embedding=vector, metadata=meta, text=chunk))
        return records

    def _persist(self) -> None:
        if not self.records:
            return
        matrix = np.vstack([rec.embedding for rec in self.records])
        meta = [rec.metadata for rec in self.records]
        texts = [rec.text for rec in self.records]
        np.save(self.embeddings_dir / "matrix.npy", matrix)
        (self.embeddings_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        (self.embeddings_dir / "texts.json").write_text(json.dumps(texts, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> None:
        matrix_path = self.embeddings_dir / "matrix.npy"
        meta_path = self.embeddings_dir / "metadata.json"
        texts_path = self.embeddings_dir / "texts.json"
        if not (matrix_path.exists() and meta_path.exists() and texts_path.exists()):
            utils.log_message("Embedding index non trovato, ricostruzione necessaria.", level="WARNING")
            self.records = []
            return
        matrix = np.load(matrix_path)
        metas = json.loads(meta_path.read_text(encoding="utf-8"))
        texts = json.loads(texts_path.read_text(encoding="utf-8"))
        self.records = [
            EmbeddingRecord(embedding=matrix[i], metadata=metas[i], text=texts[i]) for i in range(len(texts))
        ]

    def query(
        self, query: str, version: Optional[str] = None, top_k: int = 5, metadata_filter: Optional[Dict] = None
    ) -> List[EmbeddingRecord]:
        if not self.records:
            self.load()
        if not self.records:
            return []
        q_vec = _openai_embed(query, model=self.embed_model)
        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-9)
        results: List[Tuple[float, EmbeddingRecord]] = []
        for record in self.records:
            if version and record.metadata.get("version") != version:
                continue
            if metadata_filter and any(record.metadata.get(k) != v for k, v in metadata_filter.items()):
                continue
            doc_norm = record.embedding / (np.linalg.norm(record.embedding) + 1e-9)
            score = float(np.dot(q_norm, doc_norm))
            results.append((score, record))
        results.sort(key=lambda item: item[0], reverse=True)
        return [rec for _, rec in results[:top_k]]
