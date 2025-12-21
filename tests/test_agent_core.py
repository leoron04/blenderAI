from __future__ import annotations

import types

import pytest

from blenderAI import agent, cache, enterprise, rag_system, semantic_cache
from blenderAI.ai_providers import ProviderResponse


def test_suggest_returns_cached_response(monkeypatch, fake_context, tmp_path):
    cached = {"data": {"content": "cached answer", "provider": "openai", "model": "gpt-4"}}
    monkeypatch.setattr(cache, "load_cache", lambda key, cache_dir=None: cached)
    monkeypatch.setattr(cache, "save_cache", lambda *a, **k: tmp_path / "cache.json")
    audit_calls = []
    monkeypatch.setattr(enterprise.audit_logger, "log", lambda *a, **k: audit_calls.append(a))

    ai = agent.IntelligentAgent({"role": "creator", "user": "tester"})
    response = ai.suggest(fake_context, "hello world")

    assert response.cached is True
    assert response.content == "cached answer"
    assert audit_calls


def test_suggest_blocks_unauthorized_role(monkeypatch, fake_context):
    monkeypatch.setattr(enterprise, "has_access", lambda role, action: False)
    ai = agent.IntelligentAgent({"role": "viewer"})

    with pytest.raises(PermissionError):
        ai.suggest(fake_context, "generate script")


def test_suggest_uses_semantic_cache(monkeypatch, fake_context):
    monkeypatch.setattr(cache, "load_cache", lambda *a, **k: None)
    monkeypatch.setattr(rag_system, "default_rag", lambda: types.SimpleNamespace(context_as_text=lambda *a, **k: "ctx"))
    monkeypatch.setattr(semantic_cache, "lookup", lambda *a, **k: {"content": "sem hit", "provider": "semantic", "model": "gpt-4"})
    monkeypatch.setattr(enterprise.rate_limiter, "allow", lambda user: True)
    monkeypatch.setattr(enterprise.audit_logger, "log", lambda *a, **k: None)
    monkeypatch.setattr(semantic_cache, "store", lambda *a, **k: None)
    monkeypatch.setattr(semantic_cache, "update_preferences", lambda *a, **k: None)
    monkeypatch.setattr(
        agent.ai_providers,
        "try_providers",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("should not run")),
    )

    ai = agent.IntelligentAgent({"role": "creator", "semantic_cache_enabled": True, "model": "gpt-4"})
    response = ai.suggest(fake_context, "reuse previous answer")

    assert response.cached is True
    assert response.content == "sem hit"


def test_suggest_calls_provider_chain_and_caches(monkeypatch, fake_context, tmp_path):
    monkeypatch.setattr(cache, "load_cache", lambda *a, **k: None)
    monkeypatch.setattr(semantic_cache, "lookup", lambda *a, **k: None)
    monkeypatch.setattr(rag_system, "default_rag", lambda: types.SimpleNamespace(context_as_text=lambda *a, **k: "ctx"))
    saved = {}

    def _save(key, data, cache_dir=None):
        saved["payload"] = data
        return tmp_path / f"{key}.json"

    monkeypatch.setattr(cache, "save_cache", _save)
    monkeypatch.setattr(enterprise.audit_logger, "log", lambda *a, **k: None)
    provider_response = ProviderResponse(content="provider output", provider="openai", model="gpt-4", cached=False)
    monkeypatch.setattr(agent.ai_providers, "try_providers", lambda *a, **k: provider_response)

    ai = agent.IntelligentAgent({"role": "creator", "model": "gpt-4"})
    response = ai.suggest(fake_context, "fresh request")

    assert response.content == "provider output"
    assert saved["payload"]["content"] == "provider output"


def test_stub_auto_rig_returns_placeholder():
    ai = agent.IntelligentAgent({})
    stub = ai.stub_auto_rig()
    assert "Auto-rig placeholder" in stub
