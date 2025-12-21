"""Sistema RAG per fornire contesto Blender-aware alle risposte AI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

try:
    from .blender_docs_manager import DEFAULT_VERSIONS, default_manager
    from .docs_embeddings import DocsEmbeddingIndex
    from . import utils
except ImportError:  # pragma: no cover - fallback execution path
    DEFAULT_VERSIONS = ["4.2"]  # type: ignore

    class _NoopManager:  # pragma: no cover - test fallback
        def __init__(self) -> None:
            self.parsed_dir = Path("/tmp/blender_ai_docs")
            self.parsed_dir.mkdir(parents=True, exist_ok=True)

        def ingest_all(self, _versions):
            return None

        def load_entries(self, _version):
            return []

    def default_manager():  # type: ignore
        return _NoopManager()

    class DocsEmbeddingIndex:  # type: ignore
        def __init__(self, storage_dir: Path) -> None:
            self.storage_dir = Path(storage_dir)
            self.storage_dir.mkdir(parents=True, exist_ok=True)

        def build(self, _versions):
            return None

        def query(self, _query: str, version: str, top_k: int, metadata_filter=None):
            return []

    from . import utils  # type: ignore


PROMPT_TEMPLATE = (
    "Sei un esperto sviluppatore Blender Python. Usa la documentazione seguente per rispondere con accuratezza e riferimenti. "
    "Cita classi, funzioni e parametri esatti e rispetta la versione indicata."
)


class BlenderRAGSystem:
    def __init__(self, storage_dir: str | Path = "data/blender_docs", default_version: str = "4.2"):
        self.storage_dir = Path(storage_dir)
        self.default_version = default_version
        self.manager = default_manager()
        self.index = DocsEmbeddingIndex(storage_dir=self.storage_dir)
        self._ensure_seed_data()

    def _ensure_seed_data(self) -> None:
        parsed = self.manager.parsed_dir / f"{self.default_version}.json"
        if parsed.exists():
            return
        utils.log_message("Inizializzazione documentazione di base...", level="INFO")
        self.manager.ingest_all([self.default_version])
        self.index.build([self.default_version])

    def update_versions(self, versions: List[str]) -> None:
        self.manager.ingest_all(versions)
        self.index.build(versions)

    def retrieve(self, query: str, version: Optional[str] = None, top_k: int = 5, metadata_filter: Optional[Dict] = None):
        version = version or self.default_version
        return self.index.query(query, version=version, top_k=top_k, metadata_filter=metadata_filter)

    def context_payload(self, query: str, version: Optional[str] = None, top_k: int = 5) -> Dict:
        records = self.retrieve(query, version=version, top_k=top_k)
        return {
            "version": version or self.default_version,
            "prompt": PROMPT_TEMPLATE,
            "chunks": [{"text": r.text, "meta": r.metadata} for r in records],
        }

    def context_as_text(self, query: str, version: Optional[str] = None, top_k: int = 5) -> str:
        payload = self.context_payload(query, version=version, top_k=top_k)
        chunks_text = "\n\n".join(
            [f"[{idx+1}] {chunk['meta'].get('name','unknown')} ({chunk['meta']})\n{chunk['text']}" for idx, chunk in enumerate(payload["chunks"])]
        )
        return (
            f"{PROMPT_TEMPLATE}\nVersione target: {payload['version']}\n"
            f"Contesto ufficiale Blender ({len(payload['chunks'])} risultati):\n{chunks_text}"
        )

    def category_index(self) -> Dict[str, List[str]]:
        index: Dict[str, List[str]] = {}
        for version in DEFAULT_VERSIONS:
            for entry in self.manager.load_entries(version):
                index.setdefault(entry.category, []).append(entry.name)
        return index

_DEFAULT_RAG: Optional[BlenderRAGSystem] = None


def default_rag() -> BlenderRAGSystem:
    global _DEFAULT_RAG  # noqa: PLW0603
    if _DEFAULT_RAG is None:
        _DEFAULT_RAG = BlenderRAGSystem(storage_dir=os.getenv("BLENDERAI_DOCS_DIR", "data/blender_docs"))
    return _DEFAULT_RAG
