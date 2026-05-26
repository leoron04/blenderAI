"""Enterprise features: rate limiting, RBAC, audit log, exports, analytics (MVP v0.1)."""

from __future__ import annotations

import json
import os
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

import bpy

from . import utils
DEFAULT_AUDIT_PATH = utils.get_config_dir("audit.log")
DEFAULT_EXPORT_DIR = utils.get_config_dir("exports")


class RateLimiter:
    def __init__(self, limit: int = 120, window_seconds: int = 3600) -> None:
        self.limit = max(limit, 1)
        self.window_seconds = max(window_seconds, 60)
        self._events: Dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, user: str) -> bool:
        now = time.time()
        events = self._events[user]
        while events and now - events[0] > self.window_seconds:
            events.popleft()
        if len(events) >= self.limit:
            return False
        events.append(now)
        return True


class AuditLogger:
    def __init__(self, path: str = DEFAULT_AUDIT_PATH) -> None:
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def log(self, user: str, action: str, provider: str, cached: bool, project: str) -> None:
        entry = {
            "ts": time.time(),
            "user": user,
            "action": action,
            "provider": provider,
            "cached": cached,
            "project": project,
        }
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            return

    def read_entries(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []
        entries = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return []
        return entries

    def summarize(self) -> str:
        entries = self.read_entries()
        if not entries:
            return "Nessun dato audit."
        per_provider: Dict[str, int] = defaultdict(int)
        per_user: Dict[str, int] = defaultdict(int)
        for e in entries:
            per_provider[e.get("provider", "?")] += 1
            per_user[e.get("user", "?")] += 1
        lines = ["Usage Analytics:"]
        lines.append("Provider:")
        for prov, cnt in per_provider.items():
            lines.append(f"- {prov}: {cnt}")
        lines.append("Users:")
        for usr, cnt in per_user.items():
            lines.append(f"- {usr}: {cnt}")
        return "\n".join(lines)


ROLES = {
    "admin": {"generate", "export", "analyze"},
    "creator": {"generate", "export"},
    "viewer": {"export"},
}

rate_limiter = RateLimiter()
audit_logger = AuditLogger()


def has_access(role: str, action: str) -> bool:
    return action in ROLES.get(role, set())


def export_suggestion(content: str, fmt: str = "json") -> str:
    os.makedirs(DEFAULT_EXPORT_DIR, exist_ok=True)
    ts = int(time.time())
    filename = os.path.join(DEFAULT_EXPORT_DIR, f"suggestion_{ts}.{fmt}")
    payload = {"suggestion": content}
    data = json.dumps(payload, indent=2)
    if fmt == "json":
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
        return filename
    # YAML semplice (senza dipendenze esterne)
    yaml_str = "suggestion: |\n  " + "\n  ".join(content.splitlines()) + "\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(yaml_str)
    return filename


class BLENDER_AI_OT_export_suggestion(bpy.types.Operator):
    """Esporta l'ultimo suggerimento AI in JSON/YAML."""

    bl_idname = "blender_ai.export_suggestion"
    bl_label = "Export Suggestion"

    format: bpy.props.EnumProperty(
        name="Formato",
        items=[("json", "JSON", ""), ("yaml", "YAML", "")],
        default="json",
    )

    def execute(self, context):
        content = context.scene.ai_last_response
        if not content:
            self.report({"ERROR"}, "Nessun suggerimento da esportare.")
            return {"CANCELLED"}
        path = export_suggestion(content, fmt=self.format)
        context.scene.ai_export_path = path
        self.report({"INFO"}, f"Esportato su {path}")
        return {"FINISHED"}


class BLENDER_AI_OT_refresh_usage(bpy.types.Operator):
    """Aggiorna dashboard analitiche da audit log."""

    bl_idname = "blender_ai.refresh_usage"
    bl_label = "Refresh Analytics"

    def execute(self, context):
        context.scene.ai_usage_analytics = audit_logger.summarize()
        self.report({"INFO"}, "Analytics aggiornate")
        return {"FINISHED"}


class BLENDER_AI_PT_enterprise(bpy.types.Panel):
    bl_label = "🏢 Enterprise Suite"
    bl_idname = "BLENDER_AI_PT_enterprise"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.prop(scene, "ai_role", text="Role")
        box.prop(scene, "ai_rate_limit", text="Quota/h")
        box.operator(BLENDER_AI_OT_refresh_usage.bl_idname, icon="PREVIEW_RANGE")
        box.prop(scene, "ai_usage_analytics", text="Usage")

        box2 = layout.box()
        box2.label(text="Esporta ultimo suggerimento", icon="EXPORT")
        row = box2.row(align=True)
        op_json = row.operator(BLENDER_AI_OT_export_suggestion.bl_idname, text="JSON")
        op_json.format = "json"
        op_yaml = row.operator(BLENDER_AI_OT_export_suggestion.bl_idname, text="YAML")
        op_yaml.format = "yaml"
        box2.prop(scene, "ai_export_path", text="Export Path")


classes = (
    BLENDER_AI_OT_export_suggestion,
    BLENDER_AI_OT_refresh_usage,
    BLENDER_AI_PT_enterprise,
)
