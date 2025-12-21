from __future__ import annotations

import numpy as np
import pytest

from blenderAI.blender_docs_manager import DocEntry
from blenderAI.docs_embeddings import DocsEmbeddingIndex, EmbeddingRecord, chunk_entry
import blenderAI.docs_embeddings as docs_embeddings
import blenderAI.rag_system as rag_system


def test_chunk_entry_splits_long_text_and_preserves_metadata():
    entry = DocEntry(
        version="4.2",
        category="bpy",
        type="function",
        name="bpy.ops.mesh.primitive_cube_add",
        docstring="A" * 50 + "B" * 50 + "C" * 50,
    )

    chunks = chunk_entry(entry, max_chunk=60)

    assert len(chunks) > 1
    texts, metas = zip(*chunks)
    assert all(meta["version"] == "4.2" and meta["category"] == "bpy" for meta in metas)
    assert any("chunk" in meta for meta in metas)
    assert any("BBB" in text for text in texts)


def test_embedding_index_query_filters_by_version_and_metadata(tmp_docs_dir, monkeypatch):
    monkeypatch.setattr(
        docs_embeddings,
        "_openai_embed",
        lambda text, model="": np.array([1.0, 0.0]) if "camera" in text.lower() else np.array([0.0, 1.0]),
    )
    index = DocsEmbeddingIndex(storage_dir=tmp_docs_dir)
    index.records = [
        EmbeddingRecord(np.array([1.0, 0.0]), {"version": "4.2", "name": "CameraOrbit"}, "Camera orbit tip"),
        EmbeddingRecord(np.array([0.0, 1.0]), {"version": "4.2", "name": "MeshOp"}, "Mesh editing"),
        EmbeddingRecord(np.array([1.0, 0.0]), {"version": "3.6", "name": "Legacy"}, "Legacy camera data"),
    ]

    results = index.query("camera orbit path", version="4.2", top_k=2, metadata_filter={"name": "CameraOrbit"})

    assert results
    assert results[0].metadata["name"] == "CameraOrbit"
    assert all(rec.metadata["version"] == "4.2" for rec in results)


def test_context_as_text_is_version_aware_and_includes_chunks(tmp_docs_dir, monkeypatch):
    monkeypatch.setattr(rag_system.BlenderRAGSystem, "_ensure_seed_data", lambda self: None)
    rag = rag_system.BlenderRAGSystem(storage_dir=tmp_docs_dir, default_version="4.2")
    rag.index.query = lambda query, version, top_k, metadata_filter=None: [
        EmbeddingRecord(np.array([1.0]), {"name": "bpy.ops.add", "version": version}, "Adds objects"),
        EmbeddingRecord(np.array([1.0]), {"name": "bpy.ops.delete", "version": version}, "Deletes objects"),
    ]

    text = rag.context_as_text("add cube", version="4.1", top_k=2)

    assert "Versione target: 4.1" in text
    assert "bpy.ops.add" in text and "bpy.ops.delete" in text
    assert rag_system.PROMPT_TEMPLATE in text


def test_category_index_groups_entries_by_category(tmp_docs_dir, monkeypatch):
    monkeypatch.setattr(rag_system.BlenderRAGSystem, "_ensure_seed_data", lambda self: None)
    monkeypatch.setattr(rag_system, "DEFAULT_VERSIONS", ["4.2"])
    rag = rag_system.BlenderRAGSystem(storage_dir=tmp_docs_dir, default_version="4.2")
    entries = [
        DocEntry(version="4.2", category="geom", type="function", name="A", docstring=""),
        DocEntry(version="4.2", category="geom", type="class", name="B", docstring=""),
        DocEntry(version="4.2", category="render", type="function", name="C", docstring=""),
    ]
    rag.manager.load_entries = lambda version: entries

    index = rag.category_index()

    assert "geom" in index and len(index["geom"]) == 2
    assert "render" in index and index["render"] == ["C"]
