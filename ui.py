from __future__ import annotations

import bpy

from . import config
from . import node_graph_visualizer
from . import operators
from . import node_graph_visualizer


class BLENDER_AI_PT_main_panel(bpy.types.Panel):
    """Pannello principale di controllo BlenderAI."""

    bl_label = "🤖 BlenderAI Agent"
    bl_idname = "BLENDER_AI_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="⚙️ Config", icon="PREFERENCES")
        col = box.column(align=True)
        col.prop(scene, "ai_openai_key", text="OpenAI Key")
        col.prop(scene, "ai_anthropic_key", text="Claude Key")
        col.prop(scene, "ai_google_key", text="Gemini Key")
        col.prop(scene, "ai_temperature", slider=True)
        col.prop(scene, "ai_model")
        col.prop(scene, "ai_ensemble_enabled", text="Ensemble (Claude+GPT-4+Gemini)")
        col.prop(scene, "ai_ensemble_weights", text="Pesi Ensemble")
        col.prop(scene, "ai_semantic_cache_enabled", text="Semantic Cache")
        col.prop(scene, "ai_semantic_cache_threshold", slider=True)
        col.prop(scene, "ai_collab_enabled", text="Realtime Collaboration")
        if scene.ai_collab_enabled:
            col.prop(scene, "ai_collab_host", text="Host")
            col.prop(scene, "ai_collab_port", text="Port")
            col.prop(scene, "ai_collab_user", text="User")
            col.prop(scene, "ai_collab_project", text="Project")

        box = layout.box()
        box.label(text="💬 AI Suggestions", icon="WORDWRAP_ON")
        col = box.column(align=True)
        col.prop(scene, "ai_prompt", text="Prompt")
        col.operator(operators.BLENDER_AI_OT_generate_suggestions.bl_idname, icon="PLAY")
        col.label(text=f"Provider: {scene.ai_last_provider} | Model: {scene.ai_last_model} | Cache: {scene.ai_last_cached}")
        col.prop(scene, "ai_last_response", text="Response")
        col.operator("blender_ai.generate_animation", text="Generate Animation", icon="ANIM")

        box = layout.box()
        box.label(text="👁 Scene Inspector", icon="SCENE_DATA")
        col = box.column(align=True)
        col.operator(operators.BLENDER_AI_OT_analyze_scene.bl_idname, icon="VIEWZOOM")
        col.prop(scene, "ai_scene_snapshot", text="")


class BLENDER_AI_PT_code_panel(bpy.types.Panel):
    """Pannello di anteprima codice AI."""

    bl_label = "🧠 Code Generator"
    bl_idname = "BLENDER_AI_PT_code_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        scene = context.scene
        box = layout.box()
        box.label(text="Preview", icon="SCRIPT")
        row = box.row()
        col_left = row.column()
        col_left.label(text="Script")
        col_left.prop(scene, "ai_preview_code", text="")
        col_right = row.column()
        col_right.label(text="Descrizione")
        col_right.prop(scene, "ai_preview_description", text="")

        row = box.row(align=True)
        row.operator(operators.BLENDER_AI_OT_preview_code.bl_idname, text="Aggiorna Preview", icon="FILE_SCRIPT")
        row.operator(operators.BLENDER_AI_OT_apply_preview.bl_idname, text="Applica (Safe Stub)", icon="CHECKMARK")


class BLENDER_AI_PT_actions_panel(bpy.types.Panel):
    """Pannello azioni autonome stub."""

    bl_label = "🤖 Azioni Autonome"
    bl_idname = "BLENDER_AI_PT_actions_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        box = layout.box()
        box.label(text="Materiali", icon="MATERIAL")
        op_mat = box.operator(operators.BLENDER_AI_OT_auto_material.bl_idname, text="Auto Material")
        op_mat.description = "Materiale PBR auto-generato"

        box2 = layout.box()
        box2.label(text="Illuminazione", icon="LIGHT")
        box2.operator(operators.BLENDER_AI_OT_auto_light.bl_idname, text="Setup 3-Point").style = "THREE_POINT"
        box2.operator(operators.BLENDER_AI_OT_auto_light.bl_idname, text="Key Light").style = "KEY_ONLY"

        box3 = layout.box()
        box3.label(text="Rigging", icon="ARMATURE_DATA")
        box3.operator(operators.BLENDER_AI_OT_auto_rig.bl_idname, text="Auto Rig (Stub)")

        box4 = layout.box()
        box4.label(text="Geometry Nodes", icon="GEOMETRY")
        op_geo = box4.operator(operators.BLENDER_AI_OT_auto_geometry.bl_idname, text="Procedural Grid")
        op_geo.recipe = "Crea un array di cubi in griglia 5x5"


classes = (
    BLENDER_AI_PT_main_panel,
    BLENDER_AI_PT_code_panel,
    BLENDER_AI_PT_actions_panel,
    *node_graph_visualizer.classes,
)
