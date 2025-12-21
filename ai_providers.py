"""Provider layer per i modelli AI con fallback e caching locale.

Nota: le chiamate remote sono semplificate per l'ambiente di sviluppo.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import requests

from . import security_hardening
from . import utils


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

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        request_timeout: int = 30,
        rate_limit: int = 60,
        rate_window: int = 60,
    ):
        if not utils.validate_api_key(api_key):
            raise ValueError("OpenAI API key non valida.")
        self.api_key = api_key
        self.model = model
        self.timeout = request_timeout
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.rate_bucket = "openai"

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
        security_hardening.enforce_rate_limit(self.rate_bucket, self.rate_limit, self.rate_window)
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.Timeout as exc:
            raise RuntimeError("OpenAI timeout: richiesta scaduta.") from exc
        except requests.RequestException as exc:
            message = security_hardening.ensure_safe_message(str(exc), secrets=[self.api_key])
            raise RuntimeError(f"OpenAI request fallita: {message}") from exc


class AnthropicProvider:
    name = "anthropic"

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        request_timeout: int = 30,
        rate_limit: int = 60,
        rate_window: int = 60,
    ):
        if not utils.validate_api_key(api_key):
            raise ValueError("Anthropic API key non valida.")
        self.api_key = api_key
        self.model = model
        self.timeout = request_timeout
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.rate_bucket = "anthropic"

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
        security_hardening.enforce_rate_limit(self.rate_bucket, self.rate_limit, self.rate_window)
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data.get("content"):
                return data["content"][0]["text"]
            return ""
        except requests.Timeout as exc:
            raise RuntimeError("Anthropic timeout: richiesta scaduta.") from exc
        except requests.RequestException as exc:
            message = security_hardening.ensure_safe_message(str(exc), secrets=[self.api_key])
            raise RuntimeError(f"Anthropic request fallita: {message}") from exc


class GeminiProvider:
    name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-pro",
        request_timeout: int = 30,
        rate_limit: int = 60,
        rate_window: int = 60,
    ):
        if not utils.validate_api_key(api_key):
            raise ValueError("Gemini API key non valida.")
        self.api_key = api_key
        self.model = model
        self.timeout = request_timeout
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.rate_bucket = "gemini"

    def generate(self, prompt: str, system: str, temperature: float = 0.4, max_tokens: int = 800) -> str:
        url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
            "contents": [
                {"parts": [{"text": system}]},
                {"parts": [{"text": prompt}]},
            ],
        }
        security_hardening.enforce_rate_limit(self.rate_bucket, self.rate_limit, self.rate_window)
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except requests.Timeout as exc:
            raise RuntimeError("Gemini timeout: richiesta scaduta.") from exc
        except requests.RequestException as exc:
            message = security_hardening.ensure_safe_message(str(exc), secrets=[self.api_key])
            raise RuntimeError(f"Gemini request fallita: {message}") from exc


def build_provider_chain(config: Dict[str, str], priority: Optional[List[str]] = None) -> List[AIProvider]:
    """Crea la catena di fallback in base alle chiavi configurate."""
    priority = priority or ["anthropic", "openai", "gemini"]
    chain: List[AIProvider] = []
    openai_limit = int(config.get("openai_rate_limit", 60) or 60)
    openai_window = int(config.get("openai_rate_window", 60) or 60)
    anthropic_limit = int(config.get("anthropic_rate_limit", 60) or 60)
    anthropic_window = int(config.get("anthropic_rate_window", 60) or 60)
    gemini_limit = int(config.get("gemini_rate_limit", 60) or 60)
    gemini_window = int(config.get("gemini_rate_window", 60) or 60)
    request_timeout = int(config.get("request_timeout", 30) or 30)
    for provider in priority:
        if provider == "anthropic" and utils.validate_api_key(config.get("anthropic", "")):
            chain.append(
                AnthropicProvider(
                    config["anthropic"],
                    config.get("anthropic_model", "claude-3-opus-20240229"),
                    request_timeout=request_timeout,
                    rate_limit=anthropic_limit,
                    rate_window=anthropic_window,
                )
            )
        if provider == "openai" and utils.validate_api_key(config.get("openai", "")):
            chain.append(
                OpenAIProvider(
                    config["openai"],
                    config.get("openai_model", "gpt-4"),
                    request_timeout=request_timeout,
                    rate_limit=openai_limit,
                    rate_window=openai_window,
                )
            )
        if provider == "gemini" and utils.validate_api_key(config.get("google", "")):
            chain.append(
                GeminiProvider(
                    config["google"],
                    config.get("gemini_model", "gemini-pro"),
                    request_timeout=request_timeout,
                    rate_limit=gemini_limit,
                    rate_window=gemini_window,
                )
            )
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
    raise RuntimeError(f"Nessun provider disponibile: {security_hardening.ensure_safe_message(str(last_error), [])}")
