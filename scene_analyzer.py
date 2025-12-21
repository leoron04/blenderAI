"""Utility di analisi scena per BlenderAI."""

from __future__ import annotations

from typing import Any, Dict

import bpy


def fingerprint_scene(scene: bpy.types.Scene) -> str:
    counts = [len(scene.objects), len(bpy.data.materials), len(bpy.data.lights), len(bpy.data.cameras)]
    return f"{scene.name}_{'_'.join(map(str, counts))}"


def analyze_scene(context) -> Dict[str, Any]:
    scene = context.scene
    world = scene.world
    data: Dict[str, Any] = {
        "summary": {
            "objects": len(scene.objects),
            "materials": len(bpy.data.materials),
            "lights": len(bpy.data.lights),
            "cameras": len(bpy.data.cameras),
            "collections": len(bpy.data.collections),
        },
        "render": {
            "engine": scene.render.engine,
            "resolution": (scene.render.resolution_x, scene.render.resolution_y),
            "fps": scene.render.fps,
            "samples": getattr(scene.cycles, "samples", None) if scene.render.engine == "CYCLES" else None,
        },
        "world": {
            "name": world.name if world else None,
            "use_nodes": world.use_nodes if world else False,
        },
        "objects": {},
        "materials": {},
    }

    for obj in scene.objects:
        entry = {
            "type": obj.type,
            "modifiers": [m.type for m in obj.modifiers],
            "location": tuple(round(v, 4) for v in obj.location),
            "rotation": tuple(round(v, 4) for v in obj.rotation_euler),
            "scale": tuple(round(v, 4) for v in obj.scale),
            "materials": [m.name for m in getattr(obj.data, "materials", [])],
        }
        if obj.type == "MESH":
            entry["mesh"] = {
                "vertices": len(obj.data.vertices),
                "edges": len(obj.data.edges),
                "faces": len(obj.data.polygons),
            }
        data["objects"][obj.name] = entry

    for mat in bpy.data.materials:
        mat_entry = {"use_nodes": mat.use_nodes, "node_count": len(mat.node_tree.nodes) if mat.use_nodes else 0}
        data["materials"][mat.name] = mat_entry

    return data

