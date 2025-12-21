"""Agente intelligente centrale per BlenderAI."""

from __future__ import annotations

import json
from typing import Dict, Optional

from . import ai_providers
from . import cache
from . import ensemble
from . import scene_analyzer
from . import semantic_cache
from . import utils
from . import enterprise


class IntelligentAgent:
    """Coordina analisi scena, chiamate AI, caching e suggerimenti."""

    def __init__(self, config: Dict[str, str], temperature: float = 0.4, max_tokens: int = 800):
        self.config = config
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.last_scene_fingerprint: Optional[str] = None

    def _system_prompt(self, scene_payload: Dict) -> str:
        return (
            "Sei un assistente Blender senior. "
            "Analizza i dati scena forniti, proponi azioni sicure e uno script Python per Blender. "
            "Rispetta: NON applicare modifiche distruttive senza conferma. "
            "Rispondi in JSON con campi: description, script, actions[]."
            f"\n\nScene:\n{json.dumps(scene_payload, indent=2)}"
        )

    def suggest(self, context, user_prompt: str) -> ai_providers.ProviderResponse:
        scene_payload = scene_analyzer.analyze_scene(context)
        fingerprint = scene_analyzer.fingerprint_scene(context.scene)
        self.last_scene_fingerprint = fingerprint

        role = self.config.get("role", "creator")
        user = self.config.get("user", "anonymous")
        project = self.config.get("collab_project", "default")
        rate_limit = int(self.config.get("rate_limit", 120))

        enterprise.rate_limiter.limit = max(rate_limit, 1)

        if not enterprise.has_access(role, "generate"):
            raise PermissionError(f"Ruolo {role} non autorizzato a generare suggerimenti.")

        if not enterprise.rate_limiter.allow(user):
            raise RuntimeError(f"Quota esaurita per {user} (limite {rate_limit}/h).")

        ensemble_enabled = bool(self.config.get("ensemble_enabled", False))
        semantic_cache_enabled = bool(self.config.get("semantic_cache_enabled", False))
        key = cache.cache_key(
            user_prompt,
            fingerprint,
            f"{self.config.get('model', 'auto')}{'_ens' if ensemble_enabled else ''}",
        )
        cached = cache.load_cache(key)
        if cached:
            response = ai_providers.ProviderResponse(
                content=cached["data"]["content"],
                provider=cached["data"]["provider"],
                model=cached["data"]["model"],
                cached=True,
            )
            enterprise.audit_logger.log(user, "suggestion", response.provider, response.cached, project)
            return response

        if semantic_cache_enabled:
            semantic_hit = semantic_cache.lookup(
                user_prompt,
                fingerprint=fingerprint,
                model=self.config.get("model", "auto"),
                threshold=self.config.get("semantic_cache_threshold", 0.82),
            )
            if semantic_hit:
                response = ai_providers.ProviderResponse(
                    content=semantic_hit.get("content", ""),
                    provider=semantic_hit.get("provider", "semantic-cache"),
                    model=semantic_hit.get("model", self.config.get("model", "auto")),
                    cached=True,
                )
                enterprise.audit_logger.log(user, "suggestion", response.provider, response.cached, project)
                return response

        providers = ai_providers.build_provider_chain(
            {
                "anthropic": self.config.get("anthropic_key", ""),
                "anthropic_model": self.config.get("anthropic_model", "claude-3-opus-20240229"),
                "openai": self.config.get("openai_key", ""),
                "openai_model": self.config.get("openai_model", "gpt-4"),
                "google": self.config.get("google_key", ""),
                "gemini_model": self.config.get("gemini_model", "gemini-pro"),
            },
            priority=self.config.get("priority", ["anthropic", "openai", "gemini"]),
        )

        system_prompt = self._system_prompt(scene_payload)

        if ensemble_enabled:
            ensemble_cfg = ensemble.EnsembleConfig(
                enabled=True,
                weights=self.config.get("ensemble_weights", {}),
                max_models=self.config.get("ensemble_max_models", 3),
            )
            try:
                response = ensemble.run_ensemble(
                    providers,
                    prompt=user_prompt,
                    system=system_prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    cfg=ensemble_cfg,
                )
            except Exception as exc:  # noqa: BLE001
                utils.log_message(f"Ensemble error, fallback a catena: {exc}", level="WARNING")
                response = ai_providers.try_providers(
                    providers,
                    prompt=user_prompt,
                    system=system_prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
        else:
            response = ai_providers.try_providers(
                providers,
                prompt=user_prompt,
                system=system_prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

        cache.save_cache(
            key,
            {
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
            },
        )

        if semantic_cache_enabled:
            try:
                semantic_cache.store(
                    user_prompt,
                    fingerprint=fingerprint,
                    model=self.config.get("model", "auto"),
                    provider=response.provider,
                    content=response.content,
                )
                semantic_cache.update_preferences(user_prompt, response.provider)
            except Exception as exc:  # noqa: BLE001
                utils.log_message(f"Semantic cache store error: {exc}", level="WARNING")

        enterprise.audit_logger.log(user, "suggestion", response.provider, response.cached, project)
        return response

    def stub_auto_rig(self) -> str:
        """Placeholder sicuro per auto-rig."""
        return (
            "# TODO: Auto-rig placeholder\n"
            "# Questa funzione prepara un hook per future implementazioni di auto-rig.\n"
            "# Al momento non applica modifiche per sicurezza.\n"
        )
