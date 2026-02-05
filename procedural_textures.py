"""Procedural texture generation with shader nodes.

Generates complex procedural textures using Blender's shader node system:
- Noise patterns (Perlin, Voronoi, Musgrave)
- Natural materials (wood grain, marble, rust)
- Architectural (brick, tile, concrete)
- Organic (skin pores, fabric weave)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import bpy


# =============================================================================
# TEXTURE PRESETS
# =============================================================================

TEXTURE_PRESETS: Dict[str, Dict[str, Any]] = {
    "noise_clouds": {
        "description": "Soft cloud-like noise pattern",
        "nodes": [
            {"type": "ShaderNodeTexNoise", "name": "Noise", "inputs": {"Scale": 5.0, "Detail": 8.0, "Roughness": 0.5}},
        ],
        "color_ramp": [(0.0, (0.0, 0.0, 0.0, 1.0)), (1.0, (1.0, 1.0, 1.0, 1.0))],
    },
    "voronoi_cells": {
        "description": "Cellular/organic pattern",
        "nodes": [
            {"type": "ShaderNodeTexVoronoi", "name": "Voronoi", "inputs": {"Scale": 8.0}, "settings": {"feature": "F1"}},
        ],
        "color_ramp": [(0.0, (0.1, 0.1, 0.1, 1.0)), (0.5, (0.5, 0.3, 0.2, 1.0)), (1.0, (0.9, 0.85, 0.8, 1.0))],
    },
    "wood_grain": {
        "description": "Realistic wood grain pattern",
        "nodes": [
            {"type": "ShaderNodeTexWave", "name": "Wave", "inputs": {"Scale": 2.0, "Distortion": 8.0, "Detail": 3.0},
             "settings": {"wave_type": "RINGS", "rings_direction": "Z"}},
            {"type": "ShaderNodeTexNoise", "name": "Noise", "inputs": {"Scale": 15.0, "Detail": 4.0}},
        ],
        "mix_factor": 0.15,
        "color_ramp": [(0.0, (0.15, 0.08, 0.03, 1.0)), (0.4, (0.35, 0.2, 0.1, 1.0)), (0.7, (0.5, 0.3, 0.15, 1.0)), (1.0, (0.6, 0.4, 0.2, 1.0))],
    },
    "marble": {
        "description": "Marble stone veins pattern",
        "nodes": [
            {"type": "ShaderNodeTexWave", "name": "Wave", "inputs": {"Scale": 1.5, "Distortion": 4.0, "Detail": 5.0},
             "settings": {"wave_type": "BANDS"}},
            {"type": "ShaderNodeTexNoise", "name": "Noise", "inputs": {"Scale": 8.0, "Detail": 6.0, "Roughness": 0.7}},
        ],
        "mix_factor": 0.3,
        "color_ramp": [(0.0, (0.95, 0.95, 0.95, 1.0)), (0.3, (0.85, 0.85, 0.87, 1.0)), (0.6, (0.7, 0.7, 0.72, 1.0)), (1.0, (0.3, 0.3, 0.32, 1.0))],
    },
    "rust": {
        "description": "Corroded metal rust pattern",
        "nodes": [
            {"type": "ShaderNodeTexVoronoi", "name": "Voronoi", "inputs": {"Scale": 12.0}, "settings": {"feature": "F2"}},
            {"type": "ShaderNodeTexNoise", "name": "Noise", "inputs": {"Scale": 20.0, "Detail": 8.0, "Roughness": 0.8}},
        ],
        "mix_factor": 0.5,
        "color_ramp": [(0.0, (0.2, 0.1, 0.05, 1.0)), (0.3, (0.4, 0.15, 0.05, 1.0)), (0.6, (0.6, 0.25, 0.1, 1.0)), (1.0, (0.8, 0.4, 0.15, 1.0))],
        "roughness_variation": True,
    },
    "brick": {
        "description": "Brick wall pattern",
        "nodes": [
            {"type": "ShaderNodeTexBrick", "name": "Brick", "inputs": {"Scale": 4.0, "Mortar Size": 0.02, "Bias": 0.0, "Brick Width": 0.5, "Row Height": 0.25}},
        ],
        "brick_colors": {"Color1": (0.6, 0.25, 0.15, 1.0), "Color2": (0.5, 0.2, 0.12, 1.0), "Mortar": (0.7, 0.7, 0.65, 1.0)},
    },
    "concrete": {
        "description": "Rough concrete surface",
        "nodes": [
            {"type": "ShaderNodeTexNoise", "name": "Noise1", "inputs": {"Scale": 30.0, "Detail": 10.0, "Roughness": 0.6}},
            {"type": "ShaderNodeTexNoise", "name": "Noise2", "inputs": {"Scale": 100.0, "Detail": 5.0, "Roughness": 0.8}},
        ],
        "mix_factor": 0.3,
        "color_ramp": [(0.0, (0.35, 0.35, 0.35, 1.0)), (0.5, (0.5, 0.5, 0.5, 1.0)), (1.0, (0.65, 0.65, 0.65, 1.0))],
        "bump_strength": 0.3,
    },
    "fabric_weave": {
        "description": "Woven fabric texture",
        "nodes": [
            {"type": "ShaderNodeTexChecker", "name": "Checker", "inputs": {"Scale": 20.0}},
            {"type": "ShaderNodeTexNoise", "name": "Noise", "inputs": {"Scale": 50.0, "Detail": 3.0}},
        ],
        "mix_factor": 0.1,
        "color_ramp": [(0.0, (0.15, 0.2, 0.35, 1.0)), (1.0, (0.2, 0.25, 0.4, 1.0))],
    },
    "scratches": {
        "description": "Surface scratches/wear pattern",
        "nodes": [
            {"type": "ShaderNodeTexWave", "name": "Wave", "inputs": {"Scale": 50.0, "Distortion": 2.0, "Detail": 1.0},
             "settings": {"wave_type": "BANDS", "bands_direction": "X"}},
            {"type": "ShaderNodeTexNoise", "name": "Noise", "inputs": {"Scale": 100.0, "Detail": 2.0}},
        ],
        "mix_factor": 0.7,
        "color_ramp": [(0.0, (0.0, 0.0, 0.0, 1.0)), (0.8, (0.0, 0.0, 0.0, 1.0)), (1.0, (1.0, 1.0, 1.0, 1.0))],
        "use_as_mask": True,
    },
    "skin_pores": {
        "description": "Skin pore detail texture",
        "nodes": [
            {"type": "ShaderNodeTexVoronoi", "name": "Voronoi", "inputs": {"Scale": 200.0}, "settings": {"feature": "F1"}},
        ],
        "color_ramp": [(0.0, (0.0, 0.0, 0.0, 1.0)), (0.1, (0.5, 0.5, 0.5, 1.0)), (1.0, (1.0, 1.0, 1.0, 1.0))],
        "bump_strength": 0.05,
    },
    "hexagon_tiles": {
        "description": "Hexagonal tile pattern",
        "nodes": [
            {"type": "ShaderNodeTexVoronoi", "name": "Voronoi", "inputs": {"Scale": 6.0}, "settings": {"feature": "DISTANCE_TO_EDGE"}},
        ],
        "color_ramp": [(0.0, (0.1, 0.1, 0.1, 1.0)), (0.05, (0.8, 0.8, 0.8, 1.0)), (1.0, (0.9, 0.9, 0.9, 1.0))],
    },
    "gradient_radial": {
        "description": "Radial gradient from center",
        "nodes": [
            {"type": "ShaderNodeTexGradient", "name": "Gradient", "settings": {"gradient_type": "SPHERICAL"}},
        ],
        "color_ramp": [(0.0, (1.0, 1.0, 1.0, 1.0)), (1.0, (0.0, 0.0, 0.0, 1.0))],
    },
}


def _create_texture_node(nodes: bpy.types.Nodes, node_config: Dict[str, Any], x: float, y: float) -> bpy.types.Node:
    """Create a texture node with specified configuration."""
    node = nodes.new(type=node_config["type"])
    node.name = node_config.get("name", node_config["type"])
    node.location = (x, y)

    # Set input values
    for input_name, value in node_config.get("inputs", {}).items():
        if input_name in node.inputs:
            node.inputs[input_name].default_value = value

    # Set node settings
    for setting, value in node_config.get("settings", {}).items():
        if hasattr(node, setting):
            setattr(node, setting, value)

    return node


def _create_color_ramp(nodes: bpy.types.Nodes, ramp_data: List[Tuple[float, Tuple]], x: float, y: float) -> bpy.types.Node:
    """Create a color ramp node with specified stops."""
    ramp = nodes.new(type="ShaderNodeValToRGB")
    ramp.location = (x, y)

    # Clear default stops and add new ones
    color_ramp = ramp.color_ramp

    # Set first and last stops
    if len(ramp_data) >= 1:
        color_ramp.elements[0].position = ramp_data[0][0]
        color_ramp.elements[0].color = ramp_data[0][1]

    if len(ramp_data) >= 2:
        color_ramp.elements[1].position = ramp_data[-1][0]
        color_ramp.elements[1].color = ramp_data[-1][1]

    # Add intermediate stops
    for pos, color in ramp_data[1:-1]:
        elem = color_ramp.elements.new(pos)
        elem.color = color

    return ramp


def create_procedural_texture(
    material: bpy.types.Material,
    preset: str,
    connect_to: str = "Base Color"
) -> Dict[str, bpy.types.Node]:
    """Create a procedural texture and connect it to a material.

    Args:
        material: Target material with nodes enabled
        preset: Texture preset name from TEXTURE_PRESETS
        connect_to: Which BSDF input to connect (Base Color, Roughness, Normal, etc.)

    Returns:
        Dictionary of created nodes
    """
    if preset not in TEXTURE_PRESETS:
        raise ValueError(f"Unknown texture preset: {preset}")

    config = TEXTURE_PRESETS[preset]
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find Principled BSDF
    bsdf = None
    for node in nodes:
        if node.type == "BSDF_PRINCIPLED":
            bsdf = node
            break

    if not bsdf:
        raise ValueError("Material must have a Principled BSDF node")

    created_nodes = {}
    x_offset = bsdf.location[0] - 800
    y_offset = bsdf.location[1]

    # Create texture coordinate node
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (x_offset - 400, y_offset)
    created_nodes["TexCoord"] = tex_coord

    # Create mapping node for control
    mapping = nodes.new(type="ShaderNodeMapping")
    mapping.location = (x_offset - 200, y_offset)
    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
    created_nodes["Mapping"] = mapping

    # Create texture nodes
    texture_nodes = []
    for i, node_config in enumerate(config["nodes"]):
        tex_node = _create_texture_node(
            nodes, node_config,
            x_offset, y_offset - (i * 200)
        )
        links.new(mapping.outputs["Vector"], tex_node.inputs["Vector"])
        texture_nodes.append(tex_node)
        created_nodes[node_config.get("name", f"Texture{i}")] = tex_node

    # Mix textures if multiple
    output_socket = texture_nodes[0].outputs[0]  # Usually "Color" or "Fac"

    if len(texture_nodes) > 1 and "mix_factor" in config:
        mix = nodes.new(type="ShaderNodeMixRGB")
        mix.location = (x_offset + 200, y_offset)
        mix.blend_type = "MIX"
        mix.inputs["Fac"].default_value = config["mix_factor"]
        links.new(texture_nodes[0].outputs[0], mix.inputs["Color1"])
        links.new(texture_nodes[1].outputs[0], mix.inputs["Color2"])
        output_socket = mix.outputs["Color"]
        created_nodes["Mix"] = mix

    # Create color ramp if specified
    if "color_ramp" in config:
        ramp = _create_color_ramp(nodes, config["color_ramp"], x_offset + 400, y_offset)
        links.new(output_socket, ramp.inputs["Fac"])
        output_socket = ramp.outputs["Color"]
        created_nodes["ColorRamp"] = ramp

    # Handle brick colors specially
    if "brick_colors" in config and texture_nodes[0].type == "TEX_BRICK":
        brick = texture_nodes[0]
        for color_name, color_value in config["brick_colors"].items():
            if color_name in brick.inputs:
                brick.inputs[color_name].default_value = color_value
        output_socket = brick.outputs["Color"]

    # Connect to BSDF
    if connect_to in bsdf.inputs:
        links.new(output_socket, bsdf.inputs[connect_to])

    # Add bump if specified
    if config.get("bump_strength"):
        bump = nodes.new(type="ShaderNodeBump")
        bump.location = (x_offset + 400, y_offset - 300)
        bump.inputs["Strength"].default_value = config["bump_strength"]

        # Connect fac output to bump
        if "ColorRamp" in created_nodes:
            links.new(created_nodes["ColorRamp"].outputs["Color"], bump.inputs["Height"])
        else:
            links.new(texture_nodes[0].outputs[0], bump.inputs["Height"])

        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        created_nodes["Bump"] = bump

    # Add roughness variation if specified
    if config.get("roughness_variation") and "ColorRamp" in created_nodes:
        links.new(created_nodes["ColorRamp"].outputs["Color"], bsdf.inputs["Roughness"])

    return created_nodes


class BLENDER_AI_OT_procedural_texture(bpy.types.Operator):
    """Apply procedural texture to selected object's material."""

    bl_idname = "blender_ai.procedural_texture"
    bl_label = "Apply Procedural Texture"
    bl_description = "Generate procedural texture using shader nodes"
    bl_options = {"REGISTER", "UNDO"}

    preset: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Texture Preset",
        items=[
            ("noise_clouds", "Clouds", "Soft cloud-like noise"),
            ("voronoi_cells", "Cells", "Organic cellular pattern"),
            ("wood_grain", "Wood Grain", "Realistic wood"),
            ("marble", "Marble", "Stone marble veins"),
            ("rust", "Rust", "Corroded metal"),
            ("brick", "Brick", "Brick wall"),
            ("concrete", "Concrete", "Rough concrete"),
            ("fabric_weave", "Fabric", "Woven texture"),
            ("scratches", "Scratches", "Surface wear"),
            ("skin_pores", "Skin Pores", "Skin detail"),
            ("hexagon_tiles", "Hexagon Tiles", "Hex pattern"),
            ("gradient_radial", "Radial Gradient", "Center gradient"),
        ],
        default="noise_clouds",
    )

    connect_to: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Connect To",
        items=[
            ("Base Color", "Base Color", "Main color"),
            ("Roughness", "Roughness", "Surface roughness"),
            ("Metallic", "Metallic", "Metallic amount"),
            ("Emission Color", "Emission", "Glow color"),
        ],
        default="Base Color",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        obj = context.active_object

        if not obj or obj.type != "MESH":
            self.report({"ERROR"}, "Select a mesh object")
            return {"CANCELLED"}

        # Ensure material exists
        if not obj.data.materials:
            mat = bpy.data.materials.new(name=f"AI_Procedural_{self.preset}")
            mat.use_nodes = True
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]
            if not mat.use_nodes:
                mat.use_nodes = True

        try:
            created = create_procedural_texture(mat, self.preset, self.connect_to)
            self.report({"INFO"}, f"Created {len(created)} nodes for '{self.preset}' texture")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}


class BLENDER_AI_PT_procedural_textures(bpy.types.Panel):
    """Panel for procedural texture generation."""

    bl_label = "Procedural Textures"
    bl_idname = "BLENDER_AI_PT_procedural_textures"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        box = layout.box()
        box.label(text="Generate Textures", icon="TEXTURE")

        # Natural textures
        col = box.column(align=True)
        col.label(text="Natural:")
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Wood")
        op.preset = "wood_grain"
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Marble")
        op.preset = "marble"
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Rust")
        op.preset = "rust"

        # Architectural
        col.label(text="Architectural:")
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Brick")
        op.preset = "brick"
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Concrete")
        op.preset = "concrete"
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Tiles")
        op.preset = "hexagon_tiles"

        # Patterns
        col.label(text="Patterns:")
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Noise")
        op.preset = "noise_clouds"
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Cells")
        op.preset = "voronoi_cells"
        op = row.operator(BLENDER_AI_OT_procedural_texture.bl_idname, text="Fabric")
        op.preset = "fabric_weave"


classes = (
    BLENDER_AI_OT_procedural_texture,
    BLENDER_AI_PT_procedural_textures,
)
