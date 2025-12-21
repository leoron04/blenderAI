"""Agente intelligente centrale per BlenderAI."""

from __future__ import annotations

import json
from typing import Dict, Optional

from . import ai_providers
from . import cache
from . import scene_analyzer
from . import utils


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

        key = cache.cache_key(user_prompt, fingerprint, self.config.get("model", "auto"))
        cached = cache.load_cache(key)
        if cached:
            return ai_providers.ProviderResponse(
                content=cached["data"]["content"],
                provider=cached["data"]["provider"],
                model=cached["data"]["model"],
                cached=True,
            )

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

        response = ai_providers.try_providers(
            providers,
            prompt=user_prompt,
            system=self._system_prompt(scene_payload),
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
        return response

    def stub_auto_rig(self) -> str:
        """Placeholder sicuro per auto-rig."""
        return (
            "# TODO: Auto-rig placeholder\n"
            "# Questa funzione prepara un hook per future implementazioni di auto-rig.\n"
            "# Al momento non applica modifiche per sicurezza.\n"
        )

