"""Provider layer per i modelli AI con fallback e caching locale.

Nota: le chiamate remote sono semplificate per l'ambiente di sviluppo.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import requests


class AIProvider(Protocol):
    """Interfaccia minima per provider AI."""

    name: str
    model: str

    def generate(self, prompt: str, system: str, temperature: float = 0.4, max_tokens: int = 800) -> str:
        ...


@dataclass
class ProviderResponse:
    content: str
    provider: str
    model: str
    cached: bool = False


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system: str, temperature: float = 0.4, max_tokens: int = 800) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system: str, temperature: float = 0.4, max_tokens: int = 800) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        if data.get("content"):
            return data["content"][0]["text"]
        return ""


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system: str, temperature: float = 0.4, max_tokens: int = 800) -> str:
        url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
            "contents": [
                {"parts": [{"text": system}]},
                {"parts": [{"text": prompt}]},
            ],
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


def build_provider_chain(config: Dict[str, str], priority: Optional[List[str]] = None) -> List[AIProvider]:
    """Crea la catena di fallback in base alle chiavi configurate."""
    priority = priority or ["anthropic", "openai", "gemini"]
    chain: List[AIProvider] = []
    for provider in priority:
        if provider == "anthropic" and config.get("anthropic"):
            chain.append(AnthropicProvider(config["anthropic"], config.get("anthropic_model", "claude-3-opus-20240229")))
        if provider == "openai" and config.get("openai"):
            chain.append(OpenAIProvider(config["openai"], config.get("openai_model", "gpt-4")))
        if provider == "gemini" and config.get("google"):
            chain.append(GeminiProvider(config["google"], config.get("gemini_model", "gemini-pro")))
    return chain


def try_providers(
    providers: List[AIProvider],
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
) -> ProviderResponse:
    last_error: Optional[Exception] = None
    for provider in providers:
        try:
            content = provider.generate(prompt, system, temperature=temperature, max_tokens=max_tokens)
            return ProviderResponse(content=content, provider=provider.name, model=getattr(provider, "model", ""))
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"Nessun provider disponibile: {last_error}")

