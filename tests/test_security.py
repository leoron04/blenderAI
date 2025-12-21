from __future__ import annotations

import json
from pathlib import Path

import pytest

from blenderAI import cache, collaboration, enterprise, utils
from blenderAI import ai_providers


def test_validate_api_key_and_truncate_secret():
    assert utils.validate_api_key("1234567890abc")
    assert not utils.validate_api_key("short")
    secret = utils.truncate_secret("sk-1234567890", keep=2)
    assert secret.startswith("sk") and secret.endswith("90") and "3456" not in secret


def test_export_suggestion_writes_masked_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(enterprise, "DEFAULT_EXPORT_DIR", str(tmp_path / "exports"))
    payload = "render safely"

    path = enterprise.export_suggestion(payload, fmt="json")

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert data["suggestion"] == payload
    assert Path(path).suffix == ".json"


def test_build_provider_chain_ignores_missing_keys():
    chain = ai_providers.build_provider_chain({"openai": "", "anthropic": "", "google": ""}, priority=["openai", "anthropic"])
    assert chain == []


def test_cache_key_is_deterministic():
    key1 = cache.cache_key("hello", "fp", "gpt-4")
    key2 = cache.cache_key("hello", "fp", "gpt-4")
    assert key1 == key2
    assert "fp" in key1


@pytest.mark.asyncio
async def test_collaboration_broadcast_handles_empty_websockets():
    hub = collaboration.CollaborationHub()
    await hub._broadcast({"type": "noop"})


@pytest.mark.parametrize(
    "module_name",
    [
        "blenderAI.agent",
        "blenderAI.ai_providers",
        "blenderAI.animation_generator",
        "blenderAI.asset_manager",
        "blenderAI.cache",
        "blenderAI.collaboration",
        "blenderAI.config",
        "blenderAI.docs_embeddings",
        "blenderAI.blender_docs_manager",
        "blenderAI.rag_system",
        "blenderAI.scene_analyzer",
        "blenderAI.semantic_cache",
        "blenderAI.operators",
        "blenderAI.ui",
        "blenderAI.enterprise",
        "blenderAI.render_optimizer",
        "blenderAI.performance_monitor",
        "blenderAI.visualization",
        "blenderAI",
    ],
)
def test_imports_succeed(module_name):
    __import__(module_name)
