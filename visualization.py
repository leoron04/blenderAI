"""Advanced visualization helpers (overlays, keyframe preview, node heatmap)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import bpy


@dataclass
class OverlayAnnotation:
    label: str
    location: Tuple[float, float, float]
    color: Tuple[float, float, float] = (0.2, 0.7, 1.0)


def build_overlay_annotations(scene: bpy.types.Scene) -> List[OverlayAnnotation]:
    annotations: List[OverlayAnnotation] = []
    for obj in scene.objects:
        loc = tuple(round(c, 2) for c in obj.location)
        label = f"{obj.name} ({obj.type})"
        annotations.append(OverlayAnnotation(label=label, location=loc))
    return annotations[:50]


def preview_keyframes(obj: bpy.types.Object) -> str:
    if not obj:
        return "Nessun oggetto attivo."
    data_paths = obj.animation_data.action.fcurves if obj.animation_data and obj.animation_data.action else []
    if not data_paths:
        return f"{obj.name}: nessun keyframe."
    lines = []
    for curve in data_paths:
        frames = {int(p.co[0]) for p in curve.keyframe_points}
        prop = curve.data_path
        lines.append(f"{prop}: {sorted(list(frames))[:20]}")
    return "\n".join(lines)


def build_node_heatmap(scene: bpy.types.Scene) -> str:
    lines = []
    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree:
            continue
        nodes = len(mat.node_tree.nodes)
        color = "🟢" if nodes < 20 else "🟡" if nodes < 40 else "🔴"
        lines.append(f"{color} {mat.name}: {nodes} nodi")
    if not lines:
        return "Nessun materiale con nodi attivi."
    return "\n".join(lines[:50])


class BLENDER_AI_OT_refresh_visualization(bpy.types.Operator):
    """Aggiorna overlay, keyframe preview e heatmap nodi."""

    bl_idname = "blender_ai.refresh_visualization"
    bl_label = "Refresh Visualization"

    def execute(self, context):
        scene = context.scene
        annotations = build_overlay_annotations(scene)
        scene.ai_overlay_preview = "\n".join(
            f"{ann.label} @ {ann.location} color={ann.color}" for ann in annotations
        )
        scene.ai_keyframe_preview = preview_keyframes(context.active_object)
        scene.ai_node_heatmap = build_node_heatmap(scene)
        self.report({"INFO"}, "Visualizzazioni aggiornate")
        return {"FINISHED"}


class BLENDER_AI_PT_visualization(bpy.types.Panel):
    bl_label = "🛰 Advanced Visualization"
    bl_idname = "BLENDER_AI_PT_visualization"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.operator(BLENDER_AI_OT_refresh_visualization.bl_idname, icon="OVERLAY")
        box.prop(scene, "ai_overlay_preview", text="3D Overlay")

        box2 = layout.box()
        box2.label(text="Keyframe Preview", icon="ANIM")
        box2.prop(scene, "ai_keyframe_preview", text="")

        box3 = layout.box()
        box3.label(text="Node Heatmap", icon="NODE_MATERIAL")
        box3.prop(scene, "ai_node_heatmap", text="")


classes = (
    BLENDER_AI_OT_refresh_visualization,
    BLENDER_AI_PT_visualization,
)
