"""Batch render optimizer MVP v0.1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List

import bpy


def analyze_render_settings(scene: bpy.types.Scene) -> Dict[str, object]:
    samples = getattr(scene.cycles, "samples", None) if scene.render.engine == "CYCLES" else None
    denoiser = getattr(getattr(scene.cycles, "use_denoising", None), "__bool__", lambda: False)()
    return {
        "engine": scene.render.engine,
        "resolution": (scene.render.resolution_x, scene.render.resolution_y),
        "fps": scene.render.fps,
        "samples": samples,
        "denoiser": bool(denoiser),
        "recommendation": "Riduci samples a 64-128" if samples and samples > 256 else "Configurazione leggera.",
    }


def generate_batch_script(blend_files: List[str]) -> str:
    lines = ["# Batch render script (MVP)", "import bpy", "targets = ["]
    for f in blend_files:
        lines.append(f'    "{f}",')
    lines.append("]")
    lines.append("for path in targets:")
    lines.append('    print(f"Rendering {path} ...")')
    lines.append("    # bpy.ops.wm.open_mainfile(filepath=path)")
    lines.append("    # bpy.ops.render.render(animation=True)")
    return "\n".join(lines)


class BLENDER_AI_OT_optimize_render(bpy.types.Operator):
    """Analizza la scena corrente e propone ottimizzazioni render."""

    bl_idname = "blender_ai.optimize_render"
    bl_label = "Optimize Render"

    def execute(self, context):
        report = analyze_render_settings(context.scene)
        context.scene.ai_render_report = json.dumps(report, indent=2)
        self.report({"INFO"}, "Analisi render completata.")
        return {"FINISHED"}


class BLENDER_AI_OT_generate_batch_script(bpy.types.Operator):
    """Genera script batch per più scene."""

    bl_idname = "blender_ai.generate_batch_script"
    bl_label = "Generate Batch Script"

    blend_files: bpy.props.StringProperty(
        name="Blend Files",
        description="Lista di file .blend separati da virgola",
        default="file1.blend,file2.blend",
    )

    def execute(self, context):
        files = [f.strip() for f in self.blend_files.split(",") if f.strip()]
        script = generate_batch_script(files)
        context.scene.ai_batch_script = script[:4000]
        self.report({"INFO"}, "Batch script generato.")
        return {"FINISHED"}


class BLENDER_AI_PT_render_optimizer(bpy.types.Panel):
    bl_label = "🎛 Render Optimizer"
    bl_idname = "BLENDER_AI_PT_render_optimizer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.operator(BLENDER_AI_OT_optimize_render.bl_idname, icon="RENDER_STILL")
        box.prop(scene, "ai_render_report", text="Suggestions")

        batch_box = layout.box()
        batch_box.label(text="Batch Processing", icon="SEQUENCE")
        batch_box.operator(BLENDER_AI_OT_generate_batch_script.bl_idname, icon="SCRIPT")
        batch_box.prop(scene, "ai_batch_script", text="Batch Script")


classes = (
    BLENDER_AI_OT_optimize_render,
    BLENDER_AI_OT_generate_batch_script,
    BLENDER_AI_PT_render_optimizer,
)
