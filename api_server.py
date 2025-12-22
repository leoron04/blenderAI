"""Server HTTP minimale per esporre BlenderAI come API standalone.

Espone endpoint per health check e per generare suggerimenti basati
sull'agente interno, pensato per l'uso in container.
"""

from __future__ import annotations

import asyncio
import logging
import os
from types import SimpleNamespace
from typing import Any, Dict

from aiohttp import web

from .agent import IntelligentAgent

logger = logging.getLogger("blenderAI.api_server")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")


class _ApiObject:
    def __init__(self, name: str, obj_type: str = "MESH") -> None:
        self.name = name
        self.type = obj_type
        self.location = (0.0, 0.0, 0.0)
        self.rotation_euler = (0.0, 0.0, 0.0)
        self.scale = (1.0, 1.0, 1.0)
        self.modifiers = []
        self.data = SimpleNamespace(materials=[], vertices=[1], edges=[1], polygons=[1])


class _ApiRender:
    def __init__(self) -> None:
        self.engine = "CYCLES"
        self.resolution_x = 1280
        self.resolution_y = 720
        self.fps = 24


class _ApiScene:
    def __init__(self) -> None:
        self.name = "ApiScene"
        self.objects = [_ApiObject("Cube")]
        self.world = SimpleNamespace(name="World", use_nodes=False)
        self.render = _ApiRender()
        self.cycles = SimpleNamespace(samples=64)


class _ApiContext:
    def __init__(self) -> None:
        self.scene = _ApiScene()
        self.active_object = self.scene.objects[0]


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def load_config_from_env() -> Dict[str, Any]:
    """Carica configurazione API da variabili ambiente."""
    priority_raw = os.getenv("BLENDER_AI_PRIORITY", "anthropic,openai,gemini")
    priority = [p.strip() for p in priority_raw.split(",") if p.strip()]
    return {
        "openai_key": os.getenv("OPENAI_API_KEY", ""),
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "google_key": os.getenv("GOOGLE_API_KEY", ""),
        "model": os.getenv("BLENDER_AI_MODEL", "auto"),
        "role": os.getenv("BLENDER_AI_ROLE", "creator"),
        "user": os.getenv("BLENDER_AI_USER", "api"),
        "collab_project": os.getenv("BLENDER_AI_PROJECT", "api"),
        "rate_limit": int(os.getenv("BLENDER_AI_RATE_LIMIT", "120")),
        "priority": priority,
        "ensemble_enabled": _bool_env("BLENDER_AI_ENSEMBLE", False),
        "ensemble_max_models": int(os.getenv("BLENDER_AI_ENSEMBLE_MAX", "3")),
        "semantic_cache_enabled": _bool_env("BLENDER_AI_SEMANTIC_CACHE", False),
        "semantic_cache_threshold": float(os.getenv("BLENDER_AI_SEMANTIC_CACHE_THRESHOLD", "0.82")),
        "doc_version": os.getenv("BLENDER_AI_DOC_VERSION", "4.2"),
        "blender_version": os.getenv("BLENDER_AI_VERSION", "4.2"),
    }


def create_app(config: Dict[str, Any] | None = None) -> web.Application:
    cfg = config or load_config_from_env()
    agent = IntelligentAgent(cfg)

    async def health(_: web.Request) -> web.Response:
        payload = {"status": "ok", "version": os.getenv("BLENDER_AI_VERSION", "4.2")}
        return web.json_response(payload)

    async def suggest(request: web.Request) -> web.Response:
        try:
            data = await request.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Payload non valido: %s", exc)
            return web.json_response({"error": "JSON non valido"}, status=400)

        prompt = data.get("prompt") if isinstance(data, dict) else None
        if not prompt:
            return web.json_response({"error": "Campo 'prompt' mancante"}, status=400)

        context = _ApiContext()

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, agent.suggest, context, str(prompt)
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Errore durante la generazione del suggerimento")
            return web.json_response({"error": str(exc)}, status=500)

        payload = {
            "provider": response.provider,
            "model": response.model,
            "cached": getattr(response, "cached", False),
            "content": response.content,
        }
        return web.json_response(payload)

    app = web.Application()
    app.add_routes([web.get("/health", health), web.post("/api/suggest", suggest)])
    return app


def main() -> None:
    host = os.getenv("BLENDER_AI_HOST", "0.0.0.0")
    port = int(os.getenv("BLENDER_AI_PORT", "8000"))
    app = create_app()
    web.run_app(app, host=host, port=port, access_log_class=None)


if __name__ == "__main__":
    main()
