from __future__ import annotations

import bpy

from . import agent
from . import scene_analyzer
from . import utils


class BLENDER_AI_OT_generate_suggestions(bpy.types.Operator):
    """Genera suggerimenti usando la scena corrente."""

    bl_idname = "blender_ai.generate_suggestions"
    bl_label = "Generate AI Suggestions"

    prompt: bpy.props.StringProperty(name="Prompt", default="Analizza la scena e proponi miglioramenti.")

    def execute(self, context):
        scene = context.scene
        config = {
            "openai_key": scene.ai_openai_key,
            "anthropic_key": scene.ai_anthropic_key,
            "google_key": scene.ai_google_key,
            "priority": ["anthropic", "openai", "gemini"],
            "model": scene.ai_model,
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
        return {"FINISHED"}


class BLENDER_AI_OT_analyze_scene(bpy.types.Operator):
    """Esegue analisi scena e popola il pannello Scene Inspector."""

    bl_idname = "blender_ai.analyze_scene"
    bl_label = "Analyze Scene"

    def execute(self, context):
        data = scene_analyzer.analyze_scene(context)
        context.scene.ai_scene_snapshot = utils.pretty_json(data)
        self.report({"INFO"}, "Analisi scena aggiornata")
        return {"FINISHED"}


class BLENDER_AI_OT_preview_code(bpy.types.Operator):
    """Mostra il codice generato dall'AI in preview."""

    bl_idname = "blender_ai.preview_code"
    bl_label = "Preview Code"

    code: bpy.props.StringProperty(default="")
    description: bpy.props.StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        scene.ai_preview_code = self.code
        scene.ai_preview_description = self.description
        self.report({"INFO"}, "Preview aggiornata")
        return {"FINISHED"}


class BLENDER_AI_OT_apply_preview(bpy.types.Operator):
    """Applica in sicurezza lo script generato (con validazione minima)."""

    bl_idname = "blender_ai.apply_preview"
    bl_label = "Apply Preview"

    def execute(self, context):
        code = context.scene.ai_preview_code
        if not code:
            self.report({"WARNING"}, "Nessun codice in preview.")
            return {"CANCELLED"}
        utils.log_message("Esecuzione script richiesta. In ambienti sicuri, abilitare esplicitamente.")
        self.report({"INFO"}, "Preview applicata (stub sicuro, nessuna azione eseguita).")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_material(bpy.types.Operator):
    bl_idname = "blender_ai.auto_material"
    bl_label = "Auto Material"

    description: bpy.props.StringProperty(default="Materiale PBR semplice")

    def execute(self, context):
        self.report({"INFO"}, f"Auto-material stub: {self.description}")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_light(bpy.types.Operator):
    bl_idname = "blender_ai.auto_light"
    bl_label = "Auto Light Setup"

    style: bpy.props.EnumProperty(
        name="Lighting Style",
        items=[("THREE_POINT", "3-Point", ""), ("KEY_ONLY", "Key Light", "")],
        default="THREE_POINT",
    )

    def execute(self, context):
        self.report({"INFO"}, f"Setup luci '{self.style}' pronto (stub sicuro).")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_rig(bpy.types.Operator):
    bl_idname = "blender_ai.auto_rig"
    bl_label = "Auto Rig (Stub)"

    def execute(self, context):
        agent_stub = agent.IntelligentAgent({}, temperature=0.0)
        context.scene.ai_preview_code = agent_stub.stub_auto_rig()
        context.scene.ai_preview_description = "Auto-rig placeholder. Nessuna modifica applicata."
        self.report({"INFO"}, "Auto-rig stub generato.")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_geometry(bpy.types.Operator):
    bl_idname = "blender_ai.auto_geometry"
    bl_label = "Auto Geometry"

    recipe: bpy.props.StringProperty(default="Crea un array di cubi in griglia 5x5")

    def execute(self, context):
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

