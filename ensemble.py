"""Ensemble e aggregazione multi-modello (MVP v0.1).

Questo modulo implementa una logica semplice di ensemble basata su pesi
configurabili per combinare risposte da più provider (Claude, GPT-4, Gemini).
L'obiettivo è fornire una sintesi robusta mantenendo compatibilità con la
catena di fallback esistente. In caso di errori su singoli provider, il
processo continua con quelli disponibili, restituendo sempre almeno una
risposta valida.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from . import ai_providers


@dataclass
class EnsembleConfig:
    enabled: bool = False
    weights: Dict[str, float] | None = None
    max_models: int = 3

    def weight_for(self, provider: str) -> float:
        if not self.weights:
            return 1.0
        return max(self.weights.get(provider, 0.5), 0.0)


def _ranked_responses(responses: Sequence[ai_providers.ProviderResponse], weights: Dict[str, float]) -> List[ai_providers.ProviderResponse]:
    # Ordina per peso e lunghezza del contenuto per dare priorità a risposte ricche.
    return sorted(
        responses,
        key=lambda r: (weights.get(r.provider, 0.5), len(r.content)),
        reverse=True,
    )


def aggregate_responses(responses: Sequence[ai_providers.ProviderResponse], weights: Dict[str, float]) -> ai_providers.ProviderResponse:
    if not responses:
        raise ValueError("Nessuna risposta disponibile per l'ensemble")

    ranked = _ranked_responses(responses, weights)
    top = ranked[0]

    # Costruisce una sintesi leggibile mantenendo i contributi.
    parts = [f"[source={r.provider}/{r.model}] {r.content}" for r in ranked]
    combined = "\n\n".join(parts)

    return ai_providers.ProviderResponse(
        content=combined,
        provider="ensemble",
        model=f"ensemble:{top.model}",
        cached=all(r.cached for r in responses),
    )


def run_ensemble(
    providers: Sequence[ai_providers.AIProvider],
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
    cfg: EnsembleConfig,
) -> ai_providers.ProviderResponse:
    collected: List[ai_providers.ProviderResponse] = []
    weights = cfg.weights or {}

    for provider in providers[: max(cfg.max_models, 1)]:
        try:
            content = provider.generate(prompt, system, temperature=temperature, max_tokens=max_tokens)
            collected.append(
                ai_providers.ProviderResponse(
                    content=content,
                    provider=provider.name,
                    model=getattr(provider, "model", ""),
                )
            )
        except Exception:  # noqa: BLE001
            continue

    if not collected:
        raise RuntimeError("Nessuna risposta ottenuta per ensemble")

    return aggregate_responses(collected, weights)
