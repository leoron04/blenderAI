from __future__ import annotations

from typing import Any, Dict

import bpy
import json

from . import agent
from . import collaboration
from . import scene_analyzer
from . import utils


class BLENDER_AI_OT_generate_suggestions(bpy.types.Operator):
    """Genera suggerimenti usando la scena corrente.

    Args:
        context: contesto Blender corrente.

    Returns:
        {'FINISHED'} o {'CANCELLED'} in base all'esito.
    """

    bl_idname = "blender_ai.generate_suggestions"
    bl_label = "Generate AI Suggestions"

    prompt: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Prompt",
        default="Analizza la scena e proponi miglioramenti.",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene

        collaboration.ensure_started(scene.ai_collab_enabled, host=scene.ai_collab_host, port=scene.ai_collab_port)

        try:
            ensemble_weights = json.loads(scene.ai_ensemble_weights) if scene.ai_ensemble_weights else {}
            if not isinstance(ensemble_weights, dict):
                ensemble_weights = {}
        except json.JSONDecodeError:
            ensemble_weights = {}

        config: Dict[str, Any] = {
            "openai_key": scene.ai_openai_key,
            "anthropic_key": scene.ai_anthropic_key,
            "google_key": scene.ai_google_key,
            "priority": ["anthropic", "openai", "gemini"],
            "model": scene.ai_model,
            "ensemble_enabled": scene.ai_ensemble_enabled,
            "ensemble_weights": ensemble_weights,
            "semantic_cache_enabled": scene.ai_semantic_cache_enabled,
            "semantic_cache_threshold": scene.ai_semantic_cache_threshold,
            "collab_enabled": scene.ai_collab_enabled,
            "collab_user": scene.ai_collab_user,
            "collab_project": scene.ai_collab_project,
            "role": scene.ai_role,
            "rate_limit": scene.ai_rate_limit,
            "user": scene.ai_collab_user or "anonymous",
        }
        ai_agent = agent.IntelligentAgent(config, temperature=scene.ai_temperature, max_tokens=1200)
        try:
            response = ai_agent.suggest(context, self.prompt)
            scene.ai_last_response = utils.format_response(response.content, limit=3000)
            scene.ai_last_provider = response.provider
            scene.ai_last_model = response.model
            scene.ai_last_cached = response.cached
        except Exception as exc:  # noqa: BLE001
            self.report({"ERROR"}, f"AI error: {exc}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Suggerimenti da {scene.ai_last_provider} (cached={scene.ai_last_cached})")

        if scene.ai_collab_enabled:
            collaboration.broadcast_if_enabled(
                enabled=True,
                suggestion=scene.ai_last_response,
                author=scene.ai_collab_user,
                project=scene.ai_collab_project,
            )

        return {"FINISHED"}


class BLENDER_AI_OT_analyze_scene(bpy.types.Operator):
    """Esegue analisi scena e popola il pannello Scene Inspector."""

    bl_idname = "blender_ai.analyze_scene"
    bl_label = "Analyze Scene"

    def execute(self, context: bpy.types.Context) -> set[str]:
        data = scene_analyzer.analyze_scene(context)
        context.scene.ai_scene_snapshot = utils.pretty_json(data)
        self.report({"INFO"}, "Analisi scena aggiornata")
        return {"FINISHED"}


class BLENDER_AI_OT_preview_code(bpy.types.Operator):
    """Mostra il codice generato dall'AI in preview."""

    bl_idname = "blender_ai.preview_code"
    bl_label = "Preview Code"

    code: bpy.props.StringProperty = bpy.props.StringProperty(default="")
    description: bpy.props.StringProperty = bpy.props.StringProperty(default="")

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene
        scene.ai_preview_code = self.code
        scene.ai_preview_description = self.description
        self.report({"INFO"}, "Preview aggiornata")
        return {"FINISHED"}


class BLENDER_AI_OT_apply_preview(bpy.types.Operator):
    """Applica in sicurezza lo script generato (con validazione minima)."""

    bl_idname = "blender_ai.apply_preview"
    bl_label = "Apply Preview"

    def execute(self, context: bpy.types.Context) -> set[str]:
        code = context.scene.ai_preview_code
        if not code:
            self.report({"WARNING"}, "Nessun codice in preview.")
            return {"CANCELLED"}
        utils.log_message("Esecuzione script richiesta. In ambienti sicuri, abilitare esplicitamente.")
        self.report({"INFO"}, "Preview applicata (stub sicuro, nessuna azione eseguita).")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_material(bpy.types.Operator):
    """Crea materiale automatico (stub)."""

    bl_idname = "blender_ai.auto_material"
    bl_label = "Auto Material"

    description: bpy.props.StringProperty = bpy.props.StringProperty(default="Materiale PBR semplice")

    def execute(self, context: bpy.types.Context) -> set[str]:
        self.report({"INFO"}, f"Auto-material stub: {self.description}")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_light(bpy.types.Operator):
    """Crea setup luci rapido (stub)."""

    bl_idname = "blender_ai.auto_light"
    bl_label = "Auto Light Setup"

    style: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Lighting Style",
        items=[("THREE_POINT", "3-Point", ""), ("KEY_ONLY", "Key Light", "")],
        default="THREE_POINT",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        self.report({"INFO"}, f"Setup luci '{self.style}' pronto (stub sicuro).")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_rig(bpy.types.Operator):
    """Stub Auto Rig con hook futuro."""

    bl_idname = "blender_ai.auto_rig"
    bl_label = "Auto Rig (Stub)"

    def execute(self, context: bpy.types.Context) -> set[str]:
        agent_stub = agent.IntelligentAgent({}, temperature=0.0)
        context.scene.ai_preview_code = agent_stub.stub_auto_rig()
        context.scene.ai_preview_description = "Auto-rig placeholder. Nessuna modifica applicata."
        self.report({"INFO"}, "Auto-rig stub generato.")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_geometry(bpy.types.Operator):
    """Stub procedurale geometry nodes."""

    bl_idname = "blender_ai.auto_geometry"
    bl_label = "Auto Geometry"

    recipe: bpy.props.StringProperty = bpy.props.StringProperty(default="Crea un array di cubi in griglia 5x5")

    def execute(self, context: bpy.types.Context) -> set[str]:
        context.scene.ai_preview_description = f"Procedura generativa: {self.recipe}"
        self.report({"INFO"}, "Procedura geometrica (stub) pronta.")
        return {"FINISHED"}


classes = (
    BLENDER_AI_OT_generate_suggestions,
    BLENDER_AI_OT_analyze_scene,
    BLENDER_AI_OT_preview_code,
    BLENDER_AI_OT_apply_preview,
    BLENDER_AI_OT_auto_material,
    BLENDER_AI_OT_auto_light,
    BLENDER_AI_OT_auto_rig,
    BLENDER_AI_OT_auto_geometry,
)
