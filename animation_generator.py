"""Animazione guidata da prompt (MVP v0.1)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Sequence

import bpy


Keyframe = Dict[str, object]


@dataclass
class KeyframeEngine:
    """Genera sequenze di keyframe basate su prompt semplici."""

    num_frames: int = 120

    def generate(self, prompt: str) -> List[Keyframe]:
        prompt_lower = prompt.lower()
        if "walk" in prompt_lower or "forward" in prompt_lower:
            return self._walk_forward()
        if "rotate" in prompt_lower or "turn" in prompt_lower:
            return self._rotate_in_place()
        return self._walk_forward()

    def _walk_forward(self) -> List[Keyframe]:
        frames: List[Keyframe] = []
        step = 1.0 / max(self.num_frames - 1, 1)
        for i in range(self.num_frames):
            progress = i * step
            frames.append({"frame": i + 1, "property": "location", "value": (0.0, 0.0, progress * 2.0)})
        return frames

    def _rotate_in_place(self) -> List[Keyframe]:
        frames: List[Keyframe] = []
        step = 1.0 / max(self.num_frames - 1, 1)
        for i in range(self.num_frames):
            progress = i * step
            frames.append({"frame": i + 1, "property": "rotation_euler", "value": (0.0, 0.0, progress * math.radians(90))})
        return frames


@dataclass
class CameraPathGenerator:
    """Genera path camera basilari (MVP circular orbit)."""

    radius: float = 5.0
    height: float = 1.5
    frames: int = 120

    def circular_orbit(self) -> List[Keyframe]:
        keyframes: List[Keyframe] = []
        for i in range(self.frames):
            angle = 2 * math.pi * (i / max(self.frames, 1))
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            z = self.height
            keyframes.append({"frame": i + 1, "property": "location", "value": (x, y, z)})
            keyframes.append({"frame": i + 1, "property": "rotation_euler", "value": (0.0, 0.0, angle + math.pi)})
        return keyframes


def _apply_keyframes(obj: bpy.types.Object, keyframes: Sequence[Keyframe]) -> int:
    applied = 0
    for kf in keyframes:
        frame = int(kf.get("frame", 1))
        prop = str(kf.get("property", ""))
        value = kf.get("value")
        if not prop or value is None:
            continue
        if not hasattr(obj, prop):
            continue
        try:
            setattr(obj, prop, value)
            obj.keyframe_insert(data_path=prop, frame=frame)
            applied += 1
        except Exception:  # noqa: BLE001
            continue
    return applied


class BLENDER_AI_OT_generate_animation(bpy.types.Operator):
    """Crea keyframe base per animazioni guidate da prompt."""

    bl_idname = "blender_ai.generate_animation"
    bl_label = "Generate Animation"

    prompt: bpy.props.StringProperty(name="Prompt", default="walk forward")
    frame_count: bpy.props.IntProperty(name="Frames", default=120, min=2, max=10000)
    animation_type: bpy.props.EnumProperty(
        name="Animation Type",
        items=[("WALK", "Walk Forward", ""), ("ROTATE", "Rotate", ""), ("ORBIT", "Camera Orbit", "")],
        default="WALK",
    )

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({"ERROR"}, "Seleziona un oggetto o una camera.")
            return {"CANCELLED"}

        if self.animation_type == "ORBIT" and obj.type != "CAMERA":
            self.report({"ERROR"}, "L'animazione ORBIT richiede una camera selezionata.")
            return {"CANCELLED"}

        if self.animation_type == "ORBIT":
            generator = CameraPathGenerator(frames=self.frame_count)
            keyframes = generator.circular_orbit()
        else:
            engine = KeyframeEngine(num_frames=self.frame_count)
            if self.animation_type == "ROTATE":
                keyframes = engine._rotate_in_place()
            else:
                keyframes = engine._walk_forward()

        applied = _apply_keyframes(obj, keyframes)
        if applied == 0:
            self.report({"ERROR"}, "Nessun keyframe applicato.")
            return {"CANCELLED"}

        context.scene.frame_end = max(context.scene.frame_end, self.frame_count)
        self.report({"INFO"}, f"Animazione generata: {applied} keyframe.")
        return {"FINISHED"}


classes = (BLENDER_AI_OT_generate_animation,)
