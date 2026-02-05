"""Render presets for one-click scene setup.

Complete render setups including:
- Camera positioning
- Lighting configuration
- Render settings (Cycles/EEVEE)
- Output configuration
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import bpy


# =============================================================================
# RENDER PRESETS
# =============================================================================

RENDER_PRESETS: Dict[str, Dict[str, Any]] = {
    "product_shot": {
        "description": "Clean product photography setup",
        "camera": {
            "location": (3.0, -3.0, 2.5),
            "rotation": (math.radians(65), 0, math.radians(45)),
            "lens": 85,
            "dof_enabled": True,
            "dof_distance": 4.2,
            "dof_fstop": 2.8,
        },
        "lights": [
            {"type": "AREA", "name": "Key_Softbox", "location": (2, -4, 4), "rotation": (math.radians(60), 0, math.radians(25)), "energy": 800, "size": 3},
            {"type": "AREA", "name": "Fill_Light", "location": (-3, -2, 2), "rotation": (math.radians(70), 0, math.radians(-50)), "energy": 300, "size": 4},
            {"type": "AREA", "name": "Rim_Light", "location": (0, 3, 3), "rotation": (math.radians(120), 0, math.radians(180)), "energy": 400, "size": 2},
        ],
        "world": {"color": (0.9, 0.9, 0.9), "strength": 0.3},
        "render": {
            "engine": "CYCLES",
            "samples": 256,
            "resolution_x": 1920,
            "resolution_y": 1080,
            "film_transparent": True,
        },
        "ground_plane": True,
    },
    "turntable": {
        "description": "360-degree product turntable animation",
        "camera": {
            "location": (5.0, 0, 2.0),
            "rotation": (math.radians(75), 0, math.radians(90)),
            "lens": 50,
            "track_to_origin": True,
        },
        "lights": [
            {"type": "AREA", "name": "Main_Light", "location": (3, -3, 5), "rotation": (math.radians(50), 0, math.radians(35)), "energy": 1000, "size": 4},
            {"type": "AREA", "name": "Fill_Light", "location": (-4, -2, 3), "rotation": (math.radians(65), 0, math.radians(-55)), "energy": 400, "size": 5},
            {"type": "AREA", "name": "Back_Light", "location": (0, 4, 2), "rotation": (math.radians(110), 0, math.radians(180)), "energy": 300, "size": 3},
        ],
        "world": {"color": (1.0, 1.0, 1.0), "strength": 0.2},
        "render": {
            "engine": "CYCLES",
            "samples": 128,
            "resolution_x": 1080,
            "resolution_y": 1080,
        },
        "turntable_animation": {"frames": 120, "axis": "Z"},
    },
    "portrait": {
        "description": "Portrait/character lighting setup",
        "camera": {
            "location": (0, -3.5, 1.7),
            "rotation": (math.radians(90), 0, 0),
            "lens": 85,
            "dof_enabled": True,
            "dof_distance": 3.5,
            "dof_fstop": 1.8,
        },
        "lights": [
            {"type": "AREA", "name": "Key_Light", "location": (1.5, -2.5, 2.5), "rotation": (math.radians(55), 0, math.radians(30)), "energy": 600, "size": 1.5, "color": (1.0, 0.95, 0.9)},
            {"type": "AREA", "name": "Fill_Light", "location": (-2, -1.5, 1.5), "rotation": (math.radians(70), 0, math.radians(-45)), "energy": 150, "size": 3, "color": (0.9, 0.95, 1.0)},
            {"type": "SPOT", "name": "Hair_Light", "location": (-0.5, 1.5, 3), "rotation": (math.radians(140), 0, math.radians(195)), "energy": 400, "spot_size": math.radians(35)},
        ],
        "world": {"color": (0.1, 0.1, 0.12), "strength": 0.1},
        "render": {
            "engine": "CYCLES",
            "samples": 512,
            "resolution_x": 1080,
            "resolution_y": 1350,
        },
    },
    "architectural": {
        "description": "Architectural visualization with sun",
        "camera": {
            "location": (15, -15, 8),
            "rotation": (math.radians(70), 0, math.radians(45)),
            "lens": 24,
        },
        "lights": [
            {"type": "SUN", "name": "Sun", "location": (0, 0, 20), "rotation": (math.radians(50), 0, math.radians(30)), "energy": 5, "color": (1.0, 0.98, 0.95)},
        ],
        "world": {"use_sky": True, "sky_type": "NISHITA", "sun_elevation": math.radians(45), "sun_rotation": math.radians(30)},
        "render": {
            "engine": "CYCLES",
            "samples": 256,
            "resolution_x": 1920,
            "resolution_y": 1080,
        },
    },
    "studio_white": {
        "description": "Clean white studio backdrop",
        "camera": {
            "location": (4, -4, 3),
            "rotation": (math.radians(65), 0, math.radians(45)),
            "lens": 50,
        },
        "lights": [
            {"type": "AREA", "name": "Top_Light", "location": (0, 0, 6), "rotation": (math.radians(0), 0, 0), "energy": 500, "size": 8},
            {"type": "AREA", "name": "Front_Left", "location": (-4, -4, 3), "rotation": (math.radians(60), 0, math.radians(-45)), "energy": 400, "size": 4},
            {"type": "AREA", "name": "Front_Right", "location": (4, -4, 3), "rotation": (math.radians(60), 0, math.radians(45)), "energy": 400, "size": 4},
            {"type": "AREA", "name": "Background", "location": (0, 8, 4), "rotation": (math.radians(90), 0, math.radians(180)), "energy": 800, "size": 10},
        ],
        "world": {"color": (1.0, 1.0, 1.0), "strength": 0.5},
        "render": {
            "engine": "CYCLES",
            "samples": 256,
            "resolution_x": 1920,
            "resolution_y": 1080,
            "film_transparent": False,
        },
        "backdrop": True,
    },
    "dramatic_dark": {
        "description": "Dark moody lighting",
        "camera": {
            "location": (3, -4, 2),
            "rotation": (math.radians(75), 0, math.radians(35)),
            "lens": 85,
        },
        "lights": [
            {"type": "SPOT", "name": "Key_Spot", "location": (2, -3, 4), "rotation": (math.radians(55), 0, math.radians(30)), "energy": 1500, "spot_size": math.radians(25), "color": (1.0, 0.9, 0.8)},
        ],
        "world": {"color": (0.02, 0.02, 0.03), "strength": 0.05},
        "render": {
            "engine": "CYCLES",
            "samples": 512,
            "resolution_x": 1920,
            "resolution_y": 1080,
        },
    },
    "eevee_fast": {
        "description": "Fast EEVEE preview render",
        "camera": {
            "location": (4, -4, 3),
            "rotation": (math.radians(65), 0, math.radians(45)),
            "lens": 50,
        },
        "lights": [
            {"type": "AREA", "name": "Main_Light", "location": (3, -3, 5), "rotation": (math.radians(50), 0, math.radians(35)), "energy": 500, "size": 3},
            {"type": "AREA", "name": "Fill_Light", "location": (-3, -2, 2), "rotation": (math.radians(70), 0, math.radians(-50)), "energy": 200, "size": 4},
        ],
        "world": {"color": (0.5, 0.5, 0.55), "strength": 0.3},
        "render": {
            "engine": "BLENDER_EEVEE_NEXT",
            "samples": 64,
            "resolution_x": 1280,
            "resolution_y": 720,
        },
    },
}


def _create_camera(config: Dict[str, Any]) -> bpy.types.Object:
    """Create and configure camera."""
    cam_data = bpy.data.cameras.new(name="AI_Camera")
    cam_data.lens = config.get("lens", 50)

    # Depth of field
    if config.get("dof_enabled"):
        cam_data.dof.use_dof = True
        cam_data.dof.focus_distance = config.get("dof_distance", 5.0)
        cam_data.dof.aperture_fstop = config.get("dof_fstop", 2.8)

    cam_obj = bpy.data.objects.new(name="AI_Camera", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)

    cam_obj.location = config["location"]
    cam_obj.rotation_euler = config["rotation"]

    # Track to origin constraint if specified
    if config.get("track_to_origin"):
        constraint = cam_obj.constraints.new(type="TRACK_TO")
        # Create empty at origin as target
        empty = bpy.data.objects.new("AI_Camera_Target", None)
        empty.location = (0, 0, 0)
        bpy.context.collection.objects.link(empty)
        constraint.target = empty
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

    return cam_obj


def _create_light(config: Dict[str, Any]) -> bpy.types.Object:
    """Create and configure light."""
    light_data = bpy.data.lights.new(name=config["name"], type=config["type"])
    light_data.energy = config["energy"]

    if "color" in config:
        light_data.color = config["color"]

    if config["type"] == "AREA" and "size" in config:
        light_data.size = config["size"]

    if config["type"] == "SPOT" and "spot_size" in config:
        light_data.spot_size = config["spot_size"]

    light_obj = bpy.data.objects.new(name=config["name"], object_data=light_data)
    bpy.context.collection.objects.link(light_obj)

    light_obj.location = config["location"]
    light_obj.rotation_euler = config["rotation"]

    return light_obj


def _configure_world(world: bpy.types.World, config: Dict[str, Any]) -> None:
    """Configure world/environment settings."""
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    nodes.clear()

    if config.get("use_sky"):
        # Sky texture
        sky = nodes.new(type="ShaderNodeTexSky")
        sky.sky_type = config.get("sky_type", "NISHITA")
        if hasattr(sky, "sun_elevation"):
            sky.sun_elevation = config.get("sun_elevation", math.radians(45))
        if hasattr(sky, "sun_rotation"):
            sky.sun_rotation = config.get("sun_rotation", 0)

        background = nodes.new(type="ShaderNodeBackground")
        background.inputs["Strength"].default_value = config.get("strength", 1.0)

        output = nodes.new(type="ShaderNodeOutputWorld")

        links.new(sky.outputs["Color"], background.inputs["Color"])
        links.new(background.outputs["Background"], output.inputs["Surface"])
    else:
        # Solid color background
        background = nodes.new(type="ShaderNodeBackground")
        background.inputs["Color"].default_value = (*config.get("color", (0.5, 0.5, 0.5)), 1.0)
        background.inputs["Strength"].default_value = config.get("strength", 1.0)

        output = nodes.new(type="ShaderNodeOutputWorld")

        links.new(background.outputs["Background"], output.inputs["Surface"])


def _configure_render(scene: bpy.types.Scene, config: Dict[str, Any]) -> None:
    """Configure render settings."""
    scene.render.engine = config.get("engine", "CYCLES")
    scene.render.resolution_x = config.get("resolution_x", 1920)
    scene.render.resolution_y = config.get("resolution_y", 1080)

    if scene.render.engine == "CYCLES":
        scene.cycles.samples = config.get("samples", 128)
        scene.render.film_transparent = config.get("film_transparent", False)
    elif "EEVEE" in scene.render.engine:
        scene.eevee.taa_render_samples = config.get("samples", 64)


def _create_ground_plane() -> bpy.types.Object:
    """Create a ground plane for the scene."""
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "AI_Ground_Plane"

    # Create shadow catcher material
    mat = bpy.data.materials.new(name="AI_Shadow_Catcher")
    mat.use_nodes = True
    mat.shadow_method = "NONE"

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Simple diffuse for shadow catching
    diffuse = nodes.new(type="ShaderNodeBsdfDiffuse")
    diffuse.inputs["Color"].default_value = (0.9, 0.9, 0.9, 1.0)

    output = nodes.new(type="ShaderNodeOutputMaterial")
    links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])

    plane.data.materials.append(mat)

    # Enable shadow catcher in Cycles
    plane.is_shadow_catcher = True

    return plane


def _create_backdrop() -> bpy.types.Object:
    """Create a curved backdrop (cyclorama)."""
    # Create a curved plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 5, 0))
    backdrop = bpy.context.active_object
    backdrop.name = "AI_Backdrop"

    # Enter edit mode and extrude/curve
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.subdivide(number_cuts=10)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Add bend modifier
    bend = backdrop.modifiers.new(name="Curve", type="SIMPLE_DEFORM")
    bend.deform_method = "BEND"
    bend.deform_axis = "X"
    bend.angle = math.radians(90)

    # White material
    mat = bpy.data.materials.new(name="AI_Backdrop_White")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9

    backdrop.data.materials.append(mat)

    return backdrop


def _setup_turntable_animation(scene: bpy.types.Scene, config: Dict[str, Any]) -> None:
    """Setup turntable animation."""
    frames = config.get("frames", 120)
    axis = config.get("axis", "Z")

    scene.frame_start = 1
    scene.frame_end = frames

    # Find main object (first mesh that's not ground plane)
    target = None
    for obj in scene.objects:
        if obj.type == "MESH" and "AI_" not in obj.name:
            target = obj
            break

    if target:
        # Animate rotation
        axis_idx = {"X": 0, "Y": 1, "Z": 2}.get(axis, 2)

        target.rotation_euler[axis_idx] = 0
        target.keyframe_insert(data_path="rotation_euler", index=axis_idx, frame=1)

        target.rotation_euler[axis_idx] = math.radians(360)
        target.keyframe_insert(data_path="rotation_euler", index=axis_idx, frame=frames)

        # Linear interpolation
        if target.animation_data and target.animation_data.action:
            for fcurve in target.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "LINEAR"


def apply_render_preset(preset: str) -> Dict[str, Any]:
    """Apply a complete render preset to the current scene.

    Args:
        preset: Preset name from RENDER_PRESETS

    Returns:
        Dictionary with created objects and settings info
    """
    if preset not in RENDER_PRESETS:
        raise ValueError(f"Unknown render preset: {preset}")

    config = RENDER_PRESETS[preset]
    scene = bpy.context.scene
    result = {"created_objects": [], "settings": {}}

    # Create camera
    if "camera" in config:
        cam = _create_camera(config["camera"])
        scene.camera = cam
        result["created_objects"].append(cam.name)

    # Create lights
    for light_config in config.get("lights", []):
        light = _create_light(light_config)
        result["created_objects"].append(light.name)

    # Configure world
    if "world" in config:
        _configure_world(scene.world, config["world"])
        result["settings"]["world"] = "configured"

    # Configure render
    if "render" in config:
        _configure_render(scene, config["render"])
        result["settings"]["render"] = config["render"]

    # Create ground plane
    if config.get("ground_plane"):
        plane = _create_ground_plane()
        result["created_objects"].append(plane.name)

    # Create backdrop
    if config.get("backdrop"):
        backdrop = _create_backdrop()
        result["created_objects"].append(backdrop.name)

    # Setup turntable animation
    if "turntable_animation" in config:
        _setup_turntable_animation(scene, config["turntable_animation"])
        result["settings"]["animation"] = config["turntable_animation"]

    return result


class BLENDER_AI_OT_render_preset(bpy.types.Operator):
    """Apply a complete render preset to the scene."""

    bl_idname = "blender_ai.render_preset"
    bl_label = "Apply Render Preset"
    bl_description = "Setup camera, lighting, and render settings"
    bl_options = {"REGISTER", "UNDO"}

    preset: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Render Preset",
        items=[
            ("product_shot", "Product Shot", "Clean product photography"),
            ("turntable", "Turntable", "360-degree animation"),
            ("portrait", "Portrait", "Character lighting"),
            ("architectural", "Architectural", "Sun + sky for buildings"),
            ("studio_white", "Studio White", "White backdrop studio"),
            ("dramatic_dark", "Dramatic Dark", "Moody single light"),
            ("eevee_fast", "EEVEE Fast", "Quick preview render"),
        ],
        default="product_shot",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        try:
            result = apply_render_preset(self.preset)
            objects = ", ".join(result["created_objects"][:3])
            if len(result["created_objects"]) > 3:
                objects += f" (+{len(result['created_objects']) - 3} more)"
            self.report({"INFO"}, f"Applied '{self.preset}' preset: {objects}")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}


class BLENDER_AI_OT_quick_render(bpy.types.Operator):
    """Quick render with current settings."""

    bl_idname = "blender_ai.quick_render"
    bl_label = "Quick Render"
    bl_description = "Render current frame"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        bpy.ops.render.render("INVOKE_DEFAULT")
        return {"FINISHED"}


class BLENDER_AI_PT_render_presets(bpy.types.Panel):
    """Panel for render presets."""

    bl_label = "Render Presets"
    bl_idname = "BLENDER_AI_PT_render_presets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        box = layout.box()
        box.label(text="Scene Setup", icon="SCENE")

        # Product/Studio
        col = box.column(align=True)
        col.label(text="Product:")
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_render_preset.bl_idname, text="Product")
        op.preset = "product_shot"
        op = row.operator(BLENDER_AI_OT_render_preset.bl_idname, text="Turntable")
        op.preset = "turntable"
        op = row.operator(BLENDER_AI_OT_render_preset.bl_idname, text="Studio")
        op.preset = "studio_white"

        # Character/Arch
        col.label(text="Other:")
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_render_preset.bl_idname, text="Portrait")
        op.preset = "portrait"
        op = row.operator(BLENDER_AI_OT_render_preset.bl_idname, text="Arch")
        op.preset = "architectural"
        op = row.operator(BLENDER_AI_OT_render_preset.bl_idname, text="Dramatic")
        op.preset = "dramatic_dark"

        # Quick actions
        box2 = layout.box()
        box2.label(text="Quick Actions", icon="RENDER_STILL")
        row = box2.row(align=True)
        op = row.operator(BLENDER_AI_OT_render_preset.bl_idname, text="EEVEE Fast")
        op.preset = "eevee_fast"
        row.operator(BLENDER_AI_OT_quick_render.bl_idname, text="Render", icon="RENDER_STILL")


classes = (
    BLENDER_AI_OT_render_preset,
    BLENDER_AI_OT_quick_render,
    BLENDER_AI_PT_render_presets,
)
