"""Batch operations for multiple objects.

Apply operations to multiple selected objects at once:
- Material assignment
- Transform operations
- Modifier application
- Export operations
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Set, Tuple

import bpy

from . import operators


def get_selected_meshes(context: bpy.types.Context) -> List[bpy.types.Object]:
    """Get all selected mesh objects."""
    return [obj for obj in context.selected_objects if obj.type == "MESH"]


def get_selected_objects(context: bpy.types.Context, types: Optional[Set[str]] = None) -> List[bpy.types.Object]:
    """Get selected objects, optionally filtered by type."""
    if types is None:
        return list(context.selected_objects)
    return [obj for obj in context.selected_objects if obj.type in types]


class BLENDER_AI_OT_batch_material(bpy.types.Operator):
    """Apply material to all selected objects."""

    bl_idname = "blender_ai.batch_material"
    bl_label = "Batch Material"
    bl_description = "Apply material preset to all selected objects"
    bl_options = {"REGISTER", "UNDO"}

    preset: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Material Preset",
        items=[
            ("metal_gold", "Gold Metal", ""),
            ("metal_silver", "Silver Metal", ""),
            ("metal_copper", "Copper Metal", ""),
            ("plastic_glossy", "Glossy Plastic", ""),
            ("plastic_matte", "Matte Plastic", ""),
            ("glass", "Glass", ""),
            ("ceramic", "Ceramic", ""),
            ("wood", "Wood", ""),
            ("rubber", "Rubber", ""),
        ],
        default="plastic_glossy",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        meshes = get_selected_meshes(context)

        if not meshes:
            self.report({"WARNING"}, "No mesh objects selected")
            return {"CANCELLED"}

        # Get preset configuration
        preset_config = operators.MATERIAL_PRESETS.get(self.preset)
        if not preset_config:
            self.report({"ERROR"}, f"Unknown preset: {self.preset}")
            return {"CANCELLED"}

        # Create single material to share
        mat_name = f"AI_Batch_{self.preset}"
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        bsdf.location = (0, 0)

        output = nodes.new(type="ShaderNodeOutputMaterial")
        output.location = (300, 0)

        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

        # Apply preset values
        for input_name, value in preset_config.items():
            input_map = {
                "base_color": "Base Color",
                "metallic": "Metallic",
                "roughness": "Roughness",
                "specular_ior_level": "Specular IOR Level",
                "transmission_weight": "Transmission Weight",
                "ior": "IOR",
            }
            if input_name in input_map and input_map[input_name] in bsdf.inputs:
                bsdf.inputs[input_map[input_name]].default_value = value

        # Assign to all selected meshes
        count = 0
        for obj in meshes:
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
            count += 1

        self.report({"INFO"}, f"Applied '{self.preset}' to {count} objects")
        return {"FINISHED"}


class BLENDER_AI_OT_batch_transform(bpy.types.Operator):
    """Apply transform to all selected objects."""

    bl_idname = "blender_ai.batch_transform"
    bl_label = "Batch Transform"
    bl_description = "Apply transform to all selected objects"
    bl_options = {"REGISTER", "UNDO"}

    operation: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Operation",
        items=[
            ("RESET_LOCATION", "Reset Location", "Move all to origin"),
            ("RESET_ROTATION", "Reset Rotation", "Clear rotation"),
            ("RESET_SCALE", "Reset Scale", "Set scale to 1"),
            ("RESET_ALL", "Reset All", "Reset all transforms"),
            ("APPLY_TRANSFORMS", "Apply Transforms", "Apply all transforms"),
            ("CENTER_ORIGINS", "Center Origins", "Set origin to geometry center"),
            ("ORIGIN_TO_BOTTOM", "Origin to Bottom", "Set origin to bottom of mesh"),
            ("ALIGN_TO_GRID", "Align to Grid", "Snap to nearest grid"),
            ("RANDOMIZE_ROTATION", "Random Rotation", "Randomize Z rotation"),
            ("RANDOMIZE_SCALE", "Random Scale", "Randomize scale slightly"),
        ],
        default="RESET_ALL",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        objects = get_selected_objects(context)

        if not objects:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}

        import random

        count = 0
        for obj in objects:
            if self.operation == "RESET_LOCATION":
                obj.location = (0, 0, 0)
            elif self.operation == "RESET_ROTATION":
                obj.rotation_euler = (0, 0, 0)
            elif self.operation == "RESET_SCALE":
                obj.scale = (1, 1, 1)
            elif self.operation == "RESET_ALL":
                obj.location = (0, 0, 0)
                obj.rotation_euler = (0, 0, 0)
                obj.scale = (1, 1, 1)
            elif self.operation == "APPLY_TRANSFORMS":
                context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            elif self.operation == "CENTER_ORIGINS":
                context.view_layer.objects.active = obj
                bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
            elif self.operation == "ORIGIN_TO_BOTTOM":
                context.view_layer.objects.active = obj
                bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
                # Move origin to bottom
                if obj.type == "MESH":
                    bounds = [obj.matrix_world @ v.co for v in obj.data.vertices]
                    if bounds:
                        min_z = min(v.z for v in bounds)
                        obj.location.z -= (obj.location.z - min_z)
            elif self.operation == "ALIGN_TO_GRID":
                obj.location.x = round(obj.location.x)
                obj.location.y = round(obj.location.y)
                obj.location.z = round(obj.location.z)
            elif self.operation == "RANDOMIZE_ROTATION":
                obj.rotation_euler.z = random.uniform(0, math.pi * 2)
            elif self.operation == "RANDOMIZE_SCALE":
                scale_factor = random.uniform(0.8, 1.2)
                obj.scale = (obj.scale.x * scale_factor, obj.scale.y * scale_factor, obj.scale.z * scale_factor)

            count += 1

        self.report({"INFO"}, f"Applied '{self.operation}' to {count} objects")
        return {"FINISHED"}


class BLENDER_AI_OT_batch_modifier(bpy.types.Operator):
    """Add modifier to all selected objects."""

    bl_idname = "blender_ai.batch_modifier"
    bl_label = "Batch Modifier"
    bl_description = "Add modifier to all selected mesh objects"
    bl_options = {"REGISTER", "UNDO"}

    modifier_type: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Modifier",
        items=[
            ("SUBSURF", "Subdivision", "Add subdivision surface"),
            ("BEVEL", "Bevel", "Add edge bevel"),
            ("SOLIDIFY", "Solidify", "Add thickness"),
            ("MIRROR", "Mirror", "Mirror on X axis"),
            ("ARRAY", "Array", "Linear array"),
            ("DECIMATE", "Decimate", "Reduce polygons"),
            ("SMOOTH", "Smooth", "Laplacian smooth"),
            ("TRIANGULATE", "Triangulate", "Convert to triangles"),
        ],
        default="SUBSURF",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        meshes = get_selected_meshes(context)

        if not meshes:
            self.report({"WARNING"}, "No mesh objects selected")
            return {"CANCELLED"}

        count = 0
        for obj in meshes:
            mod = obj.modifiers.new(name=f"AI_{self.modifier_type}", type=self.modifier_type)

            # Configure modifier defaults
            if self.modifier_type == "SUBSURF":
                mod.levels = 2
                mod.render_levels = 2
            elif self.modifier_type == "BEVEL":
                mod.width = 0.02
                mod.segments = 2
            elif self.modifier_type == "SOLIDIFY":
                mod.thickness = 0.1
            elif self.modifier_type == "MIRROR":
                mod.use_axis[0] = True
            elif self.modifier_type == "ARRAY":
                mod.count = 3
                mod.relative_offset_displace = (1.2, 0, 0)
            elif self.modifier_type == "DECIMATE":
                mod.ratio = 0.5

            count += 1

        self.report({"INFO"}, f"Added '{self.modifier_type}' to {count} objects")
        return {"FINISHED"}


class BLENDER_AI_OT_batch_export(bpy.types.Operator):
    """Export selected objects individually."""

    bl_idname = "blender_ai.batch_export"
    bl_label = "Batch Export"
    bl_description = "Export each selected object as separate file"
    bl_options = {"REGISTER"}

    export_format: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Format",
        items=[
            ("FBX", "FBX", "Filmbox format"),
            ("OBJ", "OBJ", "Wavefront OBJ"),
            ("GLB", "GLB", "glTF Binary"),
            ("STL", "STL", "STL for 3D printing"),
        ],
        default="FBX",
    )

    export_path: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Export Path",
        default="//exports/",
        subtype="DIR_PATH",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        meshes = get_selected_meshes(context)

        if not meshes:
            self.report({"WARNING"}, "No mesh objects selected")
            return {"CANCELLED"}

        # Resolve path
        export_dir = bpy.path.abspath(self.export_path)
        os.makedirs(export_dir, exist_ok=True)

        # Store selection
        original_selection = context.selected_objects.copy()
        original_active = context.active_object

        count = 0
        for obj in meshes:
            # Select only this object
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Build filename
            filename = f"{obj.name}.{self.export_format.lower()}"
            filepath = os.path.join(export_dir, filename)

            try:
                if self.export_format == "FBX":
                    bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
                elif self.export_format == "OBJ":
                    bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)
                elif self.export_format == "GLB":
                    bpy.ops.export_scene.gltf(filepath=filepath, use_selection=True, export_format="GLB")
                elif self.export_format == "STL":
                    bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True)

                count += 1
            except Exception as e:
                self.report({"WARNING"}, f"Failed to export {obj.name}: {e}")

        # Restore selection
        bpy.ops.object.select_all(action="DESELECT")
        for obj in original_selection:
            obj.select_set(True)
        if original_active:
            context.view_layer.objects.active = original_active

        self.report({"INFO"}, f"Exported {count} objects to {export_dir}")
        return {"FINISHED"}


class BLENDER_AI_OT_batch_rename(bpy.types.Operator):
    """Rename selected objects with pattern."""

    bl_idname = "blender_ai.batch_rename"
    bl_label = "Batch Rename"
    bl_description = "Rename selected objects with pattern"
    bl_options = {"REGISTER", "UNDO"}

    base_name: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Base Name",
        default="Object",
    )

    start_number: bpy.props.IntProperty = bpy.props.IntProperty(
        name="Start Number",
        default=1,
        min=0,
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        objects = get_selected_objects(context)

        if not objects:
            self.report({"WARNING"}, "No objects selected")
            return {"CANCELLED"}

        for i, obj in enumerate(sorted(objects, key=lambda x: x.name)):
            obj.name = f"{self.base_name}_{self.start_number + i:03d}"

        self.report({"INFO"}, f"Renamed {len(objects)} objects")
        return {"FINISHED"}


class BLENDER_AI_PT_batch_operations(bpy.types.Panel):
    """Panel for batch operations."""

    bl_label = "Batch Operations"
    bl_idname = "BLENDER_AI_PT_batch_operations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        # Selection info
        meshes = get_selected_meshes(context)
        box = layout.box()
        box.label(text=f"Selected: {len(meshes)} meshes", icon="OBJECT_DATA")

        # Material batch
        box = layout.box()
        box.label(text="Batch Material", icon="MATERIAL")
        row = box.row(align=True)
        op = row.operator(BLENDER_AI_OT_batch_material.bl_idname, text="Gold")
        op.preset = "metal_gold"
        op = row.operator(BLENDER_AI_OT_batch_material.bl_idname, text="Glass")
        op.preset = "glass"
        op = row.operator(BLENDER_AI_OT_batch_material.bl_idname, text="Plastic")
        op.preset = "plastic_glossy"

        # Transform batch
        box = layout.box()
        box.label(text="Batch Transform", icon="ORIENTATION_GLOBAL")
        col = box.column(align=True)
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_batch_transform.bl_idname, text="Reset All")
        op.operation = "RESET_ALL"
        op = row.operator(BLENDER_AI_OT_batch_transform.bl_idname, text="Apply")
        op.operation = "APPLY_TRANSFORMS"
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_batch_transform.bl_idname, text="Center")
        op.operation = "CENTER_ORIGINS"
        op = row.operator(BLENDER_AI_OT_batch_transform.bl_idname, text="Random Rot")
        op.operation = "RANDOMIZE_ROTATION"

        # Modifier batch
        box = layout.box()
        box.label(text="Batch Modifier", icon="MODIFIER")
        row = box.row(align=True)
        op = row.operator(BLENDER_AI_OT_batch_modifier.bl_idname, text="Subdiv")
        op.modifier_type = "SUBSURF"
        op = row.operator(BLENDER_AI_OT_batch_modifier.bl_idname, text="Bevel")
        op.modifier_type = "BEVEL"
        op = row.operator(BLENDER_AI_OT_batch_modifier.bl_idname, text="Mirror")
        op.modifier_type = "MIRROR"

        # Export
        box = layout.box()
        box.label(text="Batch Export", icon="EXPORT")
        row = box.row(align=True)
        op = row.operator(BLENDER_AI_OT_batch_export.bl_idname, text="FBX")
        op.export_format = "FBX"
        op = row.operator(BLENDER_AI_OT_batch_export.bl_idname, text="GLB")
        op.export_format = "GLB"
        op = row.operator(BLENDER_AI_OT_batch_export.bl_idname, text="STL")
        op.export_format = "STL"


classes = (
    BLENDER_AI_OT_batch_material,
    BLENDER_AI_OT_batch_transform,
    BLENDER_AI_OT_batch_modifier,
    BLENDER_AI_OT_batch_export,
    BLENDER_AI_OT_batch_rename,
    BLENDER_AI_PT_batch_operations,
)
