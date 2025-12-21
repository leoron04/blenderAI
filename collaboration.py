"""Realtime collaboration via WebSocket (MVP v0.1)."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import Dict, List, Optional, Set

from aiohttp import web

logger = logging.getLogger("blender_ai.collab")
logger.setLevel(logging.INFO)


class CollaborationHub:
    """Gestisce connessioni WebSocket e commenti condivisi."""

    def __init__(self) -> None:
        self._websockets: Set[web.WebSocketResponse] = set()
        self._comments: List[Dict[str, str]] = []
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

    async def _ws_handler(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._websockets.add(ws)

        # invia stato iniziale
        await ws.send_json({"type": "comments:init", "data": self._comments})

        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    payload = json.loads(msg.data)
                    if payload.get("type") == "comment:add":
                        self._comments.append(payload.get("data", {}))
                        await self._broadcast({"type": "comment:new", "data": payload.get("data", {})})
                except json.JSONDecodeError:
                    continue
        self._websockets.discard(ws)
        return ws

    async def _broadcast(self, data: Dict[str, object]) -> None:
        if not self._websockets:
            return
        closed = []
        for ws in self._websockets:
            try:
                await ws.send_json(data)
            except Exception:  # noqa: BLE001
                closed.append(ws)
        for ws in closed:
            self._websockets.discard(ws)

    async def _start_async(self, host: str, port: int) -> None:
        self._app = web.Application()
        self._app.router.add_get("/ws", self._ws_handler)
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, host=host, port=port)
        await self._site.start()
        logger.info("Collaboration server avviato su ws://%s:%s/ws", host, port)

    def start(self, host: str = "0.0.0.0", port: int = 8765) -> None:
        if self._thread and self._thread.is_alive():
            return

        def _run() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self._start_async(host, port))
                self._loop.run_forever()
            except Exception as exc:  # noqa: BLE001
                logger.error("Errore server collaboration: %s", exc)
            finally:
                if self._loop and self._loop.is_running():
                    self._loop.stop()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._loop:
            return
        self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)

    def broadcast_suggestion(self, suggestion: str, author: str, project: str) -> None:
        if not self._loop or not self._loop.is_running():
            logger.info("Collaboration server non attivo, skip broadcast.")
            return
        payload = {"type": "suggestion", "data": {"author": author, "project": project, "text": suggestion}}
        asyncio.run_coroutine_threadsafe(self._broadcast(payload), self._loop)


hub = CollaborationHub()


def ensure_started(enabled: bool, host: str = "0.0.0.0", port: int = 8765) -> None:
    if enabled:
        hub.start(host, port)


def broadcast_if_enabled(enabled: bool, suggestion: str, author: str, project: str) -> None:
    try:
        if enabled:
            hub.broadcast_suggestion(suggestion, author, project)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Broadcast collaboration fallito: %s", exc)
