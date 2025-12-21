from __future__ import annotations

import numpy as np

from blenderAI.blender_docs_manager import DocEntry
from blenderAI.docs_embeddings import EmbeddingRecord
import blenderAI.rag_system as rag_system


class DummyIndex:
    def __init__(self):
        self.built = []
        self.queries = []

    def build(self, versions):
        self.built.append(tuple(versions))

    def query(self, query, version=None, top_k=5, metadata_filter=None):
        self.queries.append({"query": query, "version": version, "top_k": top_k, "metadata_filter": metadata_filter})
        return [EmbeddingRecord(np.array([1.0]), {"name": "stub", "version": version}, "text payload")]


class DummyManager:
    def __init__(self):
        self.parsed_dir = None
        self.ingested = []
        self.entries = []

    def ingest_all(self, versions):
        self.ingested.extend(list(versions))

    def load_entries(self, version):
        return self.entries


def build_rag(tmp_path, manager=None, index=None):
    manager = manager or DummyManager()
    index = index or DummyIndex()
    rag_system.BlenderRAGSystem._ensure_seed_data = lambda self: None  # type: ignore[assignment]
    rag = rag_system.BlenderRAGSystem(storage_dir=tmp_path, default_version="4.2")
    rag.manager = manager
    rag.index = index
    return rag


def test_context_payload_structure(tmp_path):
    rag = build_rag(tmp_path)
    rag.index.query = lambda query, version, top_k, metadata_filter=None: [
        EmbeddingRecord(np.array([1.0]), {"name": "Foo", "version": version}, "Sample text")
    ]

    payload = rag.context_payload("material nodes", version="4.3", top_k=1)

    assert payload["version"] == "4.3"
    assert payload["prompt"] == rag_system.PROMPT_TEMPLATE
    assert payload["chunks"][0]["meta"]["name"] == "Foo"
    assert "Sample text" in payload["chunks"][0]["text"]


def test_update_versions_ingests_and_rebuilds(tmp_path):
    manager = DummyManager()
    index = DummyIndex()
    rag = build_rag(tmp_path, manager=manager, index=index)

    rag.update_versions(["3.6", "4.0"])

    assert manager.ingested == ["3.6", "4.0"]
    assert ("3.6", "4.0") in index.built


def test_retrieve_passes_metadata_filter(tmp_path):
    index = DummyIndex()
    rag = build_rag(tmp_path, index=index)

    rag.retrieve("query", version="4.2", top_k=2, metadata_filter={"category": "bpy"})

    assert index.queries[0]["metadata_filter"] == {"category": "bpy"}
    assert index.queries[0]["top_k"] == 2
