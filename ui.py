"""BlenderAI UI Panels - Main interface for the addon.

Provides organized panels for:
- Configuration and API keys
- AI suggestions and prompts
- Scene analysis and inspection
- Code preview and execution
- Auto-generation tools (materials, lights, rigs, geometry)
"""

from __future__ import annotations

import bpy

from . import config
from . import node_graph_visualizer
from . import operators


class BLENDER_AI_PT_main_panel(bpy.types.Panel):
    """Main control panel for BlenderAI."""

    bl_label = "BlenderAI Agent"
    bl_idname = "BLENDER_AI_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        scene = context.scene

        # Configuration section
        box = layout.box()
        box.label(text="Configuration", icon="PREFERENCES")
        col = box.column(align=True)
        col.prop(scene, "ai_openai_key", text="OpenAI Key")
        col.prop(scene, "ai_anthropic_key", text="Claude Key")
        col.prop(scene, "ai_google_key", text="Gemini Key")
        col.separator()
        col.prop(scene, "ai_temperature", slider=True)
        col.prop(scene, "ai_model")

        # Advanced options (collapsible)
        box_adv = box.box()
        box_adv.label(text="Advanced Options", icon="MODIFIER")
        col_adv = box_adv.column(align=True)
        col_adv.operator("blender_ai.install_local_model", icon="SYSTEM")
        col_adv.separator()
        col_adv.prop(scene, "ai_ensemble_enabled", text="Ensemble Mode")
        if scene.ai_ensemble_enabled:
            col_adv.prop(scene, "ai_ensemble_weights", text="Weights (JSON)")
        col_adv.prop(scene, "ai_semantic_cache_enabled", text="Semantic Cache")
        if scene.ai_semantic_cache_enabled:
            col_adv.prop(scene, "ai_semantic_cache_threshold", slider=True)
        col_adv.prop(scene, "ai_collab_enabled", text="Realtime Collaboration")
        if scene.ai_collab_enabled:
            col_adv.prop(scene, "ai_collab_host", text="Host")
            col_adv.prop(scene, "ai_collab_port", text="Port")
            col_adv.prop(scene, "ai_collab_user", text="User")
            col_adv.prop(scene, "ai_collab_project", text="Project")

        # AI Suggestions section
        box = layout.box()
        box.label(text="AI Suggestions", icon="LIGHT")
        col = box.column(align=True)
        col.prop(scene, "ai_prompt", text="Prompt")
        col.operator(
            operators.BLENDER_AI_OT_generate_suggestions.bl_idname,
            text="Generate Suggestions",
            icon="PLAY",
        )

        # Response info
        if scene.ai_last_provider:
            info_box = box.box()
            row = info_box.row()
            row.label(text=f"Provider: {scene.ai_last_provider}", icon="WORLD")
            row.label(text=f"Model: {scene.ai_last_model}")
            if scene.ai_last_cached:
                info_box.label(text="(Cached response)", icon="FILE_CACHE")

        col.prop(scene, "ai_last_response", text="Response")
        col.operator(
            "blender_ai.generate_animation", text="Generate Animation", icon="ANIM"
        )

        # Scene Inspector section
        box = layout.box()
        box.label(text="Scene Inspector", icon="SCENE_DATA")
        col = box.column(align=True)
        col.operator(
            operators.BLENDER_AI_OT_analyze_scene.bl_idname,
            text="Analyze Scene",
            icon="VIEWZOOM",
        )
        if scene.ai_scene_snapshot:
            col.prop(scene, "ai_scene_snapshot", text="")


class BLENDER_AI_PT_code_panel(bpy.types.Panel):
    """Code preview and execution panel."""

    bl_label = "Code Generator"
    bl_idname = "BLENDER_AI_PT_code_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="Code Preview", icon="SCRIPT")

        # Script preview
        col = box.column(align=True)
        col.label(text="Python Script:")
        col.prop(scene, "ai_preview_code", text="")

        col.separator()
        col.label(text="Description:")
        col.prop(scene, "ai_preview_description", text="")

        # Action buttons
        row = box.row(align=True)
        row.operator(
            operators.BLENDER_AI_OT_preview_code.bl_idname,
            text="Update Preview",
            icon="FILE_REFRESH",
        )
        row.operator(
            operators.BLENDER_AI_OT_apply_preview.bl_idname,
            text="Execute Code",
            icon="PLAY",
        )

        # Safety warning
        warn = box.box()
        warn.label(text="Code is validated before execution", icon="INFO")


class BLENDER_AI_PT_actions_panel(bpy.types.Panel):
    """Auto-generation tools panel with real implementations."""

    bl_label = "Auto Tools"
    bl_idname = "BLENDER_AI_PT_actions_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # Materials section
        box = layout.box()
        box.label(text="PBR Materials", icon="MATERIAL")

        # Metal materials
        row = box.row(align=True)
        row.label(text="Metals:")
        op = row.operator(operators.BLENDER_AI_OT_auto_material.bl_idname, text="Gold")
        op.preset = "metal_gold"
        op = row.operator(
            operators.BLENDER_AI_OT_auto_material.bl_idname, text="Silver"
        )
        op.preset = "metal_silver"
        op = row.operator(
            operators.BLENDER_AI_OT_auto_material.bl_idname, text="Copper"
        )
        op.preset = "metal_copper"

        # Other materials
        row2 = box.row(align=True)
        row2.label(text="Other:")
        op = row2.operator(
            operators.BLENDER_AI_OT_auto_material.bl_idname, text="Glass"
        )
        op.preset = "glass"
        op = row2.operator(operators.BLENDER_AI_OT_auto_material.bl_idname, text="Wood")
        op.preset = "wood"
        op = row2.operator(operators.BLENDER_AI_OT_auto_material.bl_idname, text="Skin")
        op.preset = "skin"

        row3 = box.row(align=True)
        op = row3.operator(
            operators.BLENDER_AI_OT_auto_material.bl_idname, text="Plastic Glossy"
        )
        op.preset = "plastic_glossy"
        op = row3.operator(
            operators.BLENDER_AI_OT_auto_material.bl_idname, text="Emissive"
        )
        op.preset = "emissive"

        # Lighting section
        box2 = layout.box()
        box2.label(text="Lighting Setups", icon="LIGHT")

        col = box2.column(align=True)
        row = col.row(align=True)
        op = row.operator(operators.BLENDER_AI_OT_auto_light.bl_idname, text="3-Point")
        op.style = "THREE_POINT"
        op = row.operator(operators.BLENDER_AI_OT_auto_light.bl_idname, text="Studio")
        op.style = "STUDIO"
        op = row.operator(
            operators.BLENDER_AI_OT_auto_light.bl_idname, text="Rembrandt"
        )
        op.style = "REMBRANDT"

        row2 = col.row(align=True)
        op = row2.operator(
            operators.BLENDER_AI_OT_auto_light.bl_idname, text="Dramatic"
        )
        op.style = "DRAMATIC"
        op = row2.operator(operators.BLENDER_AI_OT_auto_light.bl_idname, text="Sun")
        op.style = "OUTDOOR_SUN"
        op = row2.operator(operators.BLENDER_AI_OT_auto_light.bl_idname, text="Loop")
        op.style = "LOOP"

        # Rigging section
        box3 = layout.box()
        box3.label(text="Auto Rigging", icon="ARMATURE_DATA")

        col = box3.column(align=True)
        row = col.row(align=True)
        op = row.operator(operators.BLENDER_AI_OT_auto_rig.bl_idname, text="Biped Rig")
        op.rig_type = "BIPED"
        op = row.operator(operators.BLENDER_AI_OT_auto_rig.bl_idname, text="Quadruped")
        op.rig_type = "QUADRUPED"
        op = row.operator(operators.BLENDER_AI_OT_auto_rig.bl_idname, text="Spine Only")
        op.rig_type = "SIMPLE_SPINE"

        # Geometry section
        box4 = layout.box()
        box4.label(text="Procedural Geometry", icon="MESH_GRID")

        col = box4.column(align=True)
        row = col.row(align=True)
        op = row.operator(operators.BLENDER_AI_OT_auto_geometry.bl_idname, text="Grid")
        op.pattern = "GRID"
        op = row.operator(
            operators.BLENDER_AI_OT_auto_geometry.bl_idname, text="Scatter"
        )
        op.pattern = "SCATTER"
        op = row.operator(
            operators.BLENDER_AI_OT_auto_geometry.bl_idname, text="Circular"
        )
        op.pattern = "CIRCULAR"

        row2 = col.row(align=True)
        op = row2.operator(
            operators.BLENDER_AI_OT_auto_geometry.bl_idname, text="Spiral"
        )
        op.pattern = "SPIRAL"
        op = row2.operator(operators.BLENDER_AI_OT_auto_geometry.bl_idname, text="Wave")
        op.pattern = "WAVE"


class BLENDER_AI_PT_help_panel(bpy.types.Panel):
    """Help and information panel."""

    bl_label = "Help & Info"
    bl_idname = "BLENDER_AI_PT_help_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        box = layout.box()
        box.label(text="BlenderAI v2.4.0", icon="INFO")
        col = box.column(align=True)
        col.label(text="AI-powered assistant for Blender")
        col.label(text="Supports: Claude, GPT-4, Gemini")
        col.separator()
        col.label(text="Features:", icon="CHECKMARK")
        col.label(text="  - PBR Material Generation")
        col.label(text="  - Professional Lighting")
        col.label(text="  - Auto Rigging (Biped/Quadruped)")
        col.label(text="  - Geometry Nodes Patterns")
        col.label(text="  - Safe Code Execution")


classes = (
    BLENDER_AI_PT_main_panel,
    BLENDER_AI_PT_code_panel,
    BLENDER_AI_PT_actions_panel,
    BLENDER_AI_PT_help_panel,
    *node_graph_visualizer.classes,
)
