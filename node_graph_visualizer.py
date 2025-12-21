"""Visualizzazione e suggerimenti per i node graph della scena."""

from __future__ import annotations

from typing import Dict, List, Tuple

import bpy


def _material_node_summary(material: bpy.types.Material) -> Dict[str, object]:
    nodes = material.node_tree.nodes if material.use_nodes and material.node_tree else []
    links = material.node_tree.links if material.use_nodes and material.node_tree else []
    return {
        "nodes": len(nodes),
        "links": len(links),
        "outputs": [n.name for n in nodes if getattr(n, "is_active_output", False)],
    }


def _compositor_summary(scene: bpy.types.Scene) -> Dict[str, object]:
    if not scene.use_nodes or not scene.node_tree:
        return {"enabled": False, "nodes": 0, "links": 0}
    return {
        "enabled": True,
        "nodes": len(scene.node_tree.nodes),
        "links": len(scene.node_tree.links),
        "outputs": [n.name for n in scene.node_tree.nodes if getattr(n, "is_active_output", False)],
    }


def build_node_graph_summary(scene: bpy.types.Scene) -> Tuple[str, str]:
    lines: List[str] = ["=== Shader Nodes ==="]
    suggestions: List[str] = []

    materials = [m for m in bpy.data.materials if m.use_nodes]
    if not materials:
        lines.append("Nessun materiale con nodi attivi.")
    for mat in materials:
        summary = _material_node_summary(mat)
        lines.append(f"- {mat.name}: {summary['nodes']} nodi, {summary['links']} link")
        outputs = summary["outputs"] or []
        if outputs:
            lines.append(f"  Output attivi: {', '.join(outputs)}")
        if summary["nodes"] > 40:
            suggestions.append(f"{mat.name}: valuta il grouping (oltre 40 nodi).")
        if summary["links"] == 0:
            suggestions.append(f"{mat.name}: nodi presenti ma nessun link attivo.")

    lines.append("\n=== Compositing ===")
    comp = _compositor_summary(scene)
    if comp["enabled"]:
        lines.append(f"Scene nodes: {comp['nodes']} nodi, {comp['links']} link")
        if comp["nodes"] > 30:
            suggestions.append("Compositor: considera un pre-render o nodi di mix semplificati.")
    else:
        lines.append("Compositor disattivato o senza nodi.")

    lines.append("\n=== World ===")
    if scene.world and scene.world.use_nodes and scene.world.node_tree:
        world_nodes = len(scene.world.node_tree.nodes)
        lines.append(f"World nodes: {world_nodes}")
        if world_nodes > 25:
            suggestions.append("World: riduci texture o nodi volumetrici pesanti.")
    else:
        lines.append("Nessun nodo world attivo.")

    if not suggestions:
        suggestions.append("Nessun problema evidente: graph leggero e leggibile.")

    graph_overview = "\n".join(lines)
    tips = "\n".join(f"• {s}" for s in suggestions)
    return graph_overview, tips


class BLENDER_AI_OT_refresh_node_graph(bpy.types.Operator):
    """Aggiorna l'anteprima del node graph della scena."""

    bl_idname = "blender_ai.refresh_node_graph"
    bl_label = "Refresh Node Graph"

    def execute(self, context):
        scene = context.scene
        graph_text, tips = build_node_graph_summary(scene)
        scene.ai_node_graph = graph_text[:4000]
        scene.ai_node_suggestions = tips[:2000]
        self.report({"INFO"}, "Node graph aggiornato")
        return {"FINISHED"}


class BLENDER_AI_PT_node_graph(bpy.types.Panel):
    bl_label = "🧮 Node Graph"
    bl_idname = "BLENDER_AI_PT_node_graph"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.operator(BLENDER_AI_OT_refresh_node_graph.bl_idname, icon="NODE_MATERIAL")
        box.prop(scene, "ai_node_graph", text="Node Graph")

        tips_box = layout.box()
        tips_box.label(text="Suggerimenti AI", icon="INFO")
        tips_box.prop(scene, "ai_node_suggestions", text="")


classes = (
    BLENDER_AI_OT_refresh_node_graph,
    BLENDER_AI_PT_node_graph,
)
