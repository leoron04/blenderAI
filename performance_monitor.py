"""Performance analytics dashboard MVP v0.1."""

from __future__ import annotations

import json
from typing import Dict

import bpy


def analyze_performance(scene: bpy.types.Scene) -> Dict[str, object]:
    objects = list(scene.objects)
    mesh_objs = [o for o in objects if o.type == "MESH"]
    verts = sum(len(o.data.vertices) for o in mesh_objs if getattr(o, "data", None))
    faces = sum(len(o.data.polygons) for o in mesh_objs if getattr(o, "data", None))
    materials = sum(len(getattr(o.data, "materials", [])) for o in mesh_objs if getattr(o, "data", None))
    complexity = verts + faces + materials * 10
    return {
        "objects": len(objects),
        "meshes": len(mesh_objs),
        "vertices": verts,
        "faces": faces,
        "materials": materials,
        "complexity_score": complexity,
    }


class BLENDER_AI_OT_analyze_performance(bpy.types.Operator):
    """Calcola metriche di performance della scena."""

    bl_idname = "blender_ai.analyze_performance"
    bl_label = "Analyze Performance"

    def execute(self, context):
        data = analyze_performance(context.scene)
        context.scene.ai_perf_stats = json.dumps(data, indent=2)
        self.report({"INFO"}, "Performance analizzata.")
        return {"FINISHED"}


class BLENDER_AI_PT_performance(bpy.types.Panel):
    bl_label = "📈 Performance Dashboard"
    bl_idname = "BLENDER_AI_PT_performance"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.operator(BLENDER_AI_OT_analyze_performance.bl_idname, icon="INFO")
        box.prop(scene, "ai_perf_stats", text="Stats")


classes = (
    BLENDER_AI_OT_analyze_performance,
    BLENDER_AI_PT_performance,
)
