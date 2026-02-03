"""BlenderAI Operators - Real implementations for Blender automation.

This module provides fully functional operators for:
- AI-powered suggestions generation
- Scene analysis
- PBR material creation
- Professional lighting setups
- Automatic rigging
- Procedural geometry with Geometry Nodes
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import bpy
import json

from . import agent
from . import collaboration
from . import scene_analyzer
from . import utils
from . import rag_system
from . import security_hardening


# =============================================================================
# MATERIAL PRESETS - Real PBR configurations
# =============================================================================

MATERIAL_PRESETS: Dict[str, Dict[str, Any]] = {
    "metal_gold": {
        "base_color": (1.0, 0.766, 0.336, 1.0),
        "metallic": 1.0,
        "roughness": 0.3,
        "specular_ior_level": 0.5,
    },
    "metal_silver": {
        "base_color": (0.972, 0.960, 0.915, 1.0),
        "metallic": 1.0,
        "roughness": 0.2,
        "specular_ior_level": 0.5,
    },
    "metal_copper": {
        "base_color": (0.955, 0.637, 0.538, 1.0),
        "metallic": 1.0,
        "roughness": 0.25,
        "specular_ior_level": 0.5,
    },
    "metal_iron": {
        "base_color": (0.560, 0.570, 0.580, 1.0),
        "metallic": 1.0,
        "roughness": 0.4,
        "specular_ior_level": 0.5,
    },
    "plastic_glossy": {
        "base_color": (0.8, 0.1, 0.1, 1.0),
        "metallic": 0.0,
        "roughness": 0.1,
        "specular_ior_level": 0.5,
    },
    "plastic_matte": {
        "base_color": (0.2, 0.4, 0.8, 1.0),
        "metallic": 0.0,
        "roughness": 0.7,
        "specular_ior_level": 0.3,
    },
    "rubber": {
        "base_color": (0.05, 0.05, 0.05, 1.0),
        "metallic": 0.0,
        "roughness": 0.9,
        "specular_ior_level": 0.2,
    },
    "glass": {
        "base_color": (1.0, 1.0, 1.0, 1.0),
        "metallic": 0.0,
        "roughness": 0.0,
        "transmission_weight": 1.0,
        "ior": 1.45,
    },
    "ceramic": {
        "base_color": (0.9, 0.9, 0.85, 1.0),
        "metallic": 0.0,
        "roughness": 0.3,
        "specular_ior_level": 0.6,
        "coat_weight": 0.5,
        "coat_roughness": 0.1,
    },
    "wood": {
        "base_color": (0.4, 0.26, 0.13, 1.0),
        "metallic": 0.0,
        "roughness": 0.6,
        "specular_ior_level": 0.3,
    },
    "fabric": {
        "base_color": (0.3, 0.35, 0.5, 1.0),
        "metallic": 0.0,
        "roughness": 0.8,
        "sheen_weight": 0.5,
        "sheen_roughness": 0.5,
    },
    "skin": {
        "base_color": (0.8, 0.6, 0.5, 1.0),
        "metallic": 0.0,
        "roughness": 0.5,
        "subsurface_weight": 0.3,
        "subsurface_radius": (1.0, 0.2, 0.1),
    },
    "emissive": {
        "base_color": (0.0, 0.0, 0.0, 1.0),
        "metallic": 0.0,
        "roughness": 0.5,
        "emission_color": (1.0, 0.5, 0.1, 1.0),
        "emission_strength": 10.0,
    },
}


# =============================================================================
# LIGHTING PRESETS - Professional setups
# =============================================================================

LIGHTING_PRESETS: Dict[str, List[Dict[str, Any]]] = {
    "THREE_POINT": [
        {
            "name": "Key_Light",
            "type": "AREA",
            "location": (4.0, -3.0, 5.0),
            "rotation": (math.radians(45), 0, math.radians(30)),
            "energy": 1000,
            "color": (1.0, 0.95, 0.9),
            "size": 2.0,
        },
        {
            "name": "Fill_Light",
            "type": "AREA",
            "location": (-3.0, -2.0, 3.0),
            "rotation": (math.radians(60), 0, math.radians(-45)),
            "energy": 300,
            "color": (0.9, 0.95, 1.0),
            "size": 3.0,
        },
        {
            "name": "Back_Light",
            "type": "SPOT",
            "location": (0.0, 4.0, 4.0),
            "rotation": (math.radians(135), 0, math.radians(180)),
            "energy": 500,
            "color": (1.0, 1.0, 1.0),
            "spot_size": math.radians(45),
        },
    ],
    "KEY_ONLY": [
        {
            "name": "Key_Light",
            "type": "AREA",
            "location": (4.0, -4.0, 5.0),
            "rotation": (math.radians(45), 0, math.radians(45)),
            "energy": 1500,
            "color": (1.0, 0.98, 0.95),
            "size": 3.0,
        },
    ],
    "REMBRANDT": [
        {
            "name": "Key_Light",
            "type": "AREA",
            "location": (3.0, -2.0, 4.0),
            "rotation": (math.radians(50), 0, math.radians(40)),
            "energy": 1200,
            "color": (1.0, 0.92, 0.85),
            "size": 1.5,
        },
        {
            "name": "Fill_Light",
            "type": "AREA",
            "location": (-4.0, -1.0, 2.0),
            "rotation": (math.radians(70), 0, math.radians(-60)),
            "energy": 150,
            "color": (0.85, 0.9, 1.0),
            "size": 4.0,
        },
    ],
    "LOOP": [
        {
            "name": "Key_Light",
            "type": "AREA",
            "location": (2.5, -3.0, 4.5),
            "rotation": (math.radians(45), 0, math.radians(30)),
            "energy": 1000,
            "color": (1.0, 0.96, 0.92),
            "size": 2.5,
        },
        {
            "name": "Fill_Light",
            "type": "AREA",
            "location": (-3.5, -2.0, 2.5),
            "rotation": (math.radians(65), 0, math.radians(-50)),
            "energy": 250,
            "color": (0.9, 0.95, 1.0),
            "size": 3.5,
        },
    ],
    "STUDIO": [
        {
            "name": "Main_Softbox",
            "type": "AREA",
            "location": (0.0, -5.0, 4.0),
            "rotation": (math.radians(60), 0, 0),
            "energy": 800,
            "color": (1.0, 1.0, 1.0),
            "size": 4.0,
        },
        {
            "name": "Left_Fill",
            "type": "AREA",
            "location": (-4.0, -2.0, 2.0),
            "rotation": (math.radians(70), 0, math.radians(-60)),
            "energy": 400,
            "color": (1.0, 1.0, 1.0),
            "size": 2.0,
        },
        {
            "name": "Right_Fill",
            "type": "AREA",
            "location": (4.0, -2.0, 2.0),
            "rotation": (math.radians(70), 0, math.radians(60)),
            "energy": 400,
            "color": (1.0, 1.0, 1.0),
            "size": 2.0,
        },
        {
            "name": "Background",
            "type": "AREA",
            "location": (0.0, 5.0, 3.0),
            "rotation": (math.radians(90), 0, math.radians(180)),
            "energy": 200,
            "color": (0.95, 0.95, 1.0),
            "size": 6.0,
        },
    ],
    "DRAMATIC": [
        {
            "name": "Key_Light",
            "type": "SPOT",
            "location": (3.0, -3.0, 5.0),
            "rotation": (math.radians(45), 0, math.radians(30)),
            "energy": 2000,
            "color": (1.0, 0.85, 0.7),
            "spot_size": math.radians(30),
        },
    ],
    "OUTDOOR_SUN": [
        {
            "name": "Sun",
            "type": "SUN",
            "location": (0.0, 0.0, 10.0),
            "rotation": (math.radians(45), 0, math.radians(30)),
            "energy": 5,
            "color": (1.0, 0.98, 0.95),
        },
    ],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_target_object(context: bpy.types.Context) -> Optional[bpy.types.Object]:
    """Get the target object for operations (active or first selected mesh)."""
    if context.active_object and context.active_object.type == "MESH":
        return context.active_object
    for obj in context.selected_objects:
        if obj.type == "MESH":
            return obj
    return None


def _create_light(
    name: str,
    light_type: str,
    location: Tuple[float, float, float],
    rotation: Tuple[float, float, float],
    energy: float,
    color: Tuple[float, float, float],
    **kwargs
) -> bpy.types.Object:
    """Create a light with specified properties."""
    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_data.energy = energy
    light_data.color = color

    # Type-specific properties
    if light_type == "AREA" and "size" in kwargs:
        light_data.size = kwargs["size"]
    if light_type == "SPOT" and "spot_size" in kwargs:
        light_data.spot_size = kwargs["spot_size"]

    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = location
    light_object.rotation_euler = rotation

    return light_object


def _validate_code_safety(code: str) -> Tuple[bool, str]:
    """Validate code for dangerous patterns before execution."""
    dangerous_patterns = [
        (r'\bos\.system\b', "os.system calls are not allowed"),
        (r'\bsubprocess\b', "subprocess module is not allowed"),
        (r'\beval\s*\(', "eval() is not allowed"),
        (r'\bexec\s*\(', "nested exec() is not allowed"),
        (r'\b__import__\b', "__import__ is not allowed"),
        (r'\bopen\s*\([^)]*["\']w', "file writing is not allowed"),
        (r'\brm\s+-rf\b', "dangerous shell commands detected"),
        (r'\bshutil\.rmtree\b', "shutil.rmtree is not allowed"),
        (r'\bimport\s+socket\b', "socket module is not allowed"),
        (r'\bimport\s+http\b', "http module is not allowed"),
        (r'\bimport\s+urllib\b', "urllib module is not allowed"),
        (r'\bimport\s+requests\b', "requests module is not allowed"),
    ]

    for pattern, message in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, message

    # Check for reasonable code length
    if len(code) > 50000:
        return False, "Code too long (max 50000 characters)"

    return True, "OK"


# =============================================================================
# OPERATOR CLASSES
# =============================================================================

class BLENDER_AI_OT_generate_suggestions(bpy.types.Operator):
    """Generate AI-powered suggestions for the current scene.

    Analyzes the scene context and uses configured AI providers to generate
    intelligent suggestions for improvements, optimizations, or creative ideas.
    """

    bl_idname = "blender_ai.generate_suggestions"
    bl_label = "Generate AI Suggestions"
    bl_options = {"REGISTER", "UNDO"}

    prompt: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Prompt",
        default="Analizza la scena e proponi miglioramenti.",
        description="Prompt to send to the AI",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene

        try:
            prompt = security_hardening.sanitize_user_input(self.prompt, "Prompt", max_length=1200)
            collab_host = security_hardening.sanitize_user_input(
                scene.ai_collab_host, "Collab host", max_length=255, allow_empty=True
            ) or "127.0.0.1"
            collab_port = security_hardening.validate_port(scene.ai_collab_port, "Collab port")
            collab_user = security_hardening.sanitize_user_input(
                scene.ai_collab_user, "User", max_length=64, allow_empty=True
            ) or "anonymous"
            collab_project = security_hardening.sanitize_user_input(
                scene.ai_collab_project, "Project", max_length=64, allow_empty=True
            ) or "default"
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        collaboration.ensure_started(scene.ai_collab_enabled, host=collab_host, port=collab_port)

        try:
            ensemble_weights = json.loads(scene.ai_ensemble_weights) if scene.ai_ensemble_weights else {}
            if not isinstance(ensemble_weights, dict):
                ensemble_weights = {}
        except json.JSONDecodeError:
            ensemble_weights = {}

        env_keys, env_errors = security_hardening.validate_environment()
        for error in env_errors:
            utils.log_message(error, level="WARNING")

        config: Dict[str, Any] = {
            "openai_key": env_keys.get("openai_api_key", ""),
            "anthropic_key": env_keys.get("anthropic_api_key", ""),
            "google_key": env_keys.get("google_api_key", ""),
            "priority": ["anthropic", "openai", "gemini"],
            "model": scene.ai_model,
            "blender_version": scene.ai_blender_version,
            "ensemble_enabled": scene.ai_ensemble_enabled,
            "ensemble_weights": ensemble_weights,
            "semantic_cache_enabled": scene.ai_semantic_cache_enabled,
            "semantic_cache_threshold": scene.ai_semantic_cache_threshold,
            "collab_enabled": scene.ai_collab_enabled,
            "collab_user": collab_user,
            "collab_project": collab_project,
            "role": scene.ai_role,
            "rate_limit": scene.ai_rate_limit,
            "user": collab_user,
            "request_timeout": 45,
            "openai_rate_limit": scene.ai_rate_limit,
            "openai_rate_window": 3600,
            "anthropic_rate_limit": scene.ai_rate_limit,
            "anthropic_rate_window": 3600,
            "gemini_rate_limit": scene.ai_rate_limit,
            "gemini_rate_window": 3600,
        }
        ai_agent = agent.IntelligentAgent(config, temperature=scene.ai_temperature, max_tokens=1200)
        try:
            rag = rag_system.default_rag()
            scene.ai_doc_context = rag.context_as_text(prompt, version=scene.ai_blender_version, top_k=5)
            scene.ai_doc_hints = utils.pretty_json(
                scene_analyzer.doc_hints_for_scene(context, version=scene.ai_blender_version)
            )
            response = ai_agent.suggest(context, prompt)
            scene.ai_last_response = utils.format_response(response.content, limit=3000)
            scene.ai_last_provider = response.provider
            scene.ai_last_model = response.model
            scene.ai_last_cached = response.cached
        except Exception as exc:  # noqa: BLE001
            safe_error = security_hardening.ensure_safe_message(str(exc), secrets=[])
            self.report({"ERROR"}, f"AI error: {safe_error}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Suggerimenti da {scene.ai_last_provider} (cached={scene.ai_last_cached})")

        if scene.ai_collab_enabled:
            collaboration.broadcast_if_enabled(
                enabled=True,
                suggestion=scene.ai_last_response,
                author=scene.ai_collab_user,
                project=scene.ai_collab_project,
            )

        return {"FINISHED"}


class BLENDER_AI_OT_analyze_scene(bpy.types.Operator):
    """Perform deep scene analysis and populate the Scene Inspector panel."""

    bl_idname = "blender_ai.analyze_scene"
    bl_label = "Analyze Scene"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        data = scene_analyzer.analyze_scene(context)
        context.scene.ai_scene_snapshot = utils.pretty_json(data)
        self.report({"INFO"}, "Analisi scena aggiornata")
        return {"FINISHED"}


class BLENDER_AI_OT_preview_code(bpy.types.Operator):
    """Preview AI-generated code before execution."""

    bl_idname = "blender_ai.preview_code"
    bl_label = "Preview Code"
    bl_description = "Preview the generated code"
    bl_options = {"REGISTER"}

    code: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Code",
        default="",
        description="Python code to preview",
    )
    description: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Description",
        default="",
        description="Description of what the code does",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene
        scene.ai_preview_code = self.code
        scene.ai_preview_description = self.description
        self.report({"INFO"}, "Preview aggiornata")
        return {"FINISHED"}


class BLENDER_AI_OT_apply_preview(bpy.types.Operator):
    """Safely execute the previewed code with validation.

    Performs security checks before execution:
    - Validates code against dangerous patterns
    - Limits execution scope to bpy operations
    - Provides error handling and rollback hints
    """

    bl_idname = "blender_ai.apply_preview"
    bl_label = "Apply Preview"
    bl_description = "Execute the previewed code after safety validation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        code = context.scene.ai_preview_code
        if not code or not code.strip():
            self.report({"WARNING"}, "Nessun codice in preview.")
            return {"CANCELLED"}

        # Security validation
        is_safe, message = _validate_code_safety(code)
        if not is_safe:
            self.report({"ERROR"}, f"Codice non sicuro: {message}")
            return {"CANCELLED"}

        # Prepare safe execution environment
        safe_globals = {
            "bpy": bpy,
            "math": math,
            "Vector": None,  # Will be set if mathutils available
            "Matrix": None,
            "Euler": None,
        }

        try:
            from mathutils import Vector, Matrix, Euler
            safe_globals["Vector"] = Vector
            safe_globals["Matrix"] = Matrix
            safe_globals["Euler"] = Euler
        except ImportError:
            pass

        safe_globals["__builtins__"] = {
            "range": range,
            "len": len,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "True": True,
            "False": False,
            "None": None,
            "print": print,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "sum": sum,
            "sorted": sorted,
            "reversed": reversed,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
        }

        try:
            exec(code, safe_globals, {})
            utils.log_message("Script eseguito con successo", level="INFO")
            self.report({"INFO"}, "Script eseguito con successo!")
            return {"FINISHED"}
        except Exception as exc:  # noqa: BLE001
            error_msg = security_hardening.ensure_safe_message(str(exc), secrets=[])
            utils.log_message(f"Errore esecuzione script: {error_msg}", level="ERROR")
            self.report({"ERROR"}, f"Errore: {error_msg}")
            return {"CANCELLED"}


class BLENDER_AI_OT_auto_material(bpy.types.Operator):
    """Create a real PBR material with Principled BSDF shader.

    Supports multiple material presets:
    - Metal (gold, silver, copper, iron)
    - Plastic (glossy, matte)
    - Glass, ceramic, wood, fabric, skin
    - Emissive materials
    """

    bl_idname = "blender_ai.auto_material"
    bl_label = "Auto Material"
    bl_description = "Create a PBR material with Principled BSDF"
    bl_options = {"REGISTER", "UNDO"}

    preset: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Material Preset",
        items=[
            ("metal_gold", "Gold Metal", "Shiny gold metal"),
            ("metal_silver", "Silver Metal", "Polished silver"),
            ("metal_copper", "Copper Metal", "Warm copper tone"),
            ("metal_iron", "Iron Metal", "Industrial iron"),
            ("plastic_glossy", "Glossy Plastic", "Shiny plastic surface"),
            ("plastic_matte", "Matte Plastic", "Diffuse plastic"),
            ("rubber", "Rubber", "Dark rubber material"),
            ("glass", "Glass", "Transparent glass"),
            ("ceramic", "Ceramic", "Glazed ceramic"),
            ("wood", "Wood", "Natural wood"),
            ("fabric", "Fabric", "Cloth/textile"),
            ("skin", "Skin", "Human skin with SSS"),
            ("emissive", "Emissive", "Glowing material"),
        ],
        default="plastic_glossy",
    )

    material_name: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Material Name",
        default="",
        description="Custom name for the material (auto-generated if empty)",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        obj = _get_target_object(context)

        # Get preset configuration
        preset_config = MATERIAL_PRESETS.get(self.preset, MATERIAL_PRESETS["plastic_glossy"])

        # Generate material name
        mat_name = self.material_name if self.material_name else f"AI_{self.preset}"

        # Create new material
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True

        # Get node tree
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Clear default nodes
        nodes.clear()

        # Create Principled BSDF
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        bsdf.location = (0, 0)

        # Create Material Output
        output = nodes.new(type="ShaderNodeOutputMaterial")
        output.location = (300, 0)

        # Connect BSDF to Output
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

        # Apply preset values to BSDF inputs
        for input_name, value in preset_config.items():
            if input_name == "base_color":
                bsdf.inputs["Base Color"].default_value = value
            elif input_name == "metallic":
                bsdf.inputs["Metallic"].default_value = value
            elif input_name == "roughness":
                bsdf.inputs["Roughness"].default_value = value
            elif input_name == "specular_ior_level":
                bsdf.inputs["Specular IOR Level"].default_value = value
            elif input_name == "transmission_weight":
                bsdf.inputs["Transmission Weight"].default_value = value
            elif input_name == "ior":
                bsdf.inputs["IOR"].default_value = value
            elif input_name == "coat_weight":
                bsdf.inputs["Coat Weight"].default_value = value
            elif input_name == "coat_roughness":
                bsdf.inputs["Coat Roughness"].default_value = value
            elif input_name == "sheen_weight":
                bsdf.inputs["Sheen Weight"].default_value = value
            elif input_name == "sheen_roughness":
                bsdf.inputs["Sheen Roughness"].default_value = value
            elif input_name == "subsurface_weight":
                bsdf.inputs["Subsurface Weight"].default_value = value
            elif input_name == "subsurface_radius":
                bsdf.inputs["Subsurface Radius"].default_value = value
            elif input_name == "emission_color":
                bsdf.inputs["Emission Color"].default_value = value
            elif input_name == "emission_strength":
                bsdf.inputs["Emission Strength"].default_value = value

        # Assign to active object if exists
        if obj:
            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
            self.report({"INFO"}, f"Materiale '{mat_name}' creato e assegnato a '{obj.name}'")
        else:
            self.report({"INFO"}, f"Materiale '{mat_name}' creato (nessun oggetto selezionato)")

        return {"FINISHED"}


class BLENDER_AI_OT_auto_light(bpy.types.Operator):
    """Create professional lighting setups.

    Available presets:
    - THREE_POINT: Classic key/fill/back setup
    - KEY_ONLY: Single dramatic key light
    - REMBRANDT: Classic portrait lighting
    - LOOP: Soft portrait lighting
    - STUDIO: Full studio setup with 4 lights
    - DRAMATIC: High contrast single spot
    - OUTDOOR_SUN: Simulated sunlight
    """

    bl_idname = "blender_ai.auto_light"
    bl_label = "Auto Light Setup"
    bl_description = "Create a professional lighting setup"
    bl_options = {"REGISTER", "UNDO"}

    style: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Lighting Style",
        items=[
            ("THREE_POINT", "3-Point Classic", "Key, fill, and back light"),
            ("KEY_ONLY", "Key Light Only", "Single key light"),
            ("REMBRANDT", "Rembrandt", "Classic portrait lighting"),
            ("LOOP", "Loop Lighting", "Soft loop pattern"),
            ("STUDIO", "Studio Setup", "Full 4-light studio"),
            ("DRAMATIC", "Dramatic", "High contrast spot"),
            ("OUTDOOR_SUN", "Outdoor Sun", "Sunlight simulation"),
        ],
        default="THREE_POINT",
    )

    energy_multiplier: bpy.props.FloatProperty = bpy.props.FloatProperty(
        name="Energy Multiplier",
        default=1.0,
        min=0.1,
        max=10.0,
        description="Scale all light energies",
    )

    clear_existing: bpy.props.BoolProperty = bpy.props.BoolProperty(
        name="Clear Existing Lights",
        default=False,
        description="Remove existing lights before creating new ones",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        # Optionally clear existing lights
        if self.clear_existing:
            lights_to_remove = [obj for obj in bpy.data.objects if obj.type == "LIGHT"]
            for light in lights_to_remove:
                bpy.data.objects.remove(light, do_unlink=True)

        # Get preset configuration
        preset_lights = LIGHTING_PRESETS.get(self.style, LIGHTING_PRESETS["THREE_POINT"])

        created_lights = []
        for light_config in preset_lights:
            name = light_config["name"]
            light_type = light_config["type"]
            location = light_config["location"]
            rotation = light_config["rotation"]
            energy = light_config["energy"] * self.energy_multiplier
            color = light_config["color"]

            # Extra kwargs for specific light types
            kwargs = {}
            if "size" in light_config:
                kwargs["size"] = light_config["size"]
            if "spot_size" in light_config:
                kwargs["spot_size"] = light_config["spot_size"]

            light_obj = _create_light(name, light_type, location, rotation, energy, color, **kwargs)
            created_lights.append(light_obj.name)

        self.report({"INFO"}, f"Setup '{self.style}' creato: {', '.join(created_lights)}")
        return {"FINISHED"}


class BLENDER_AI_OT_auto_rig(bpy.types.Operator):
    """Create a basic armature rig for the selected mesh.

    Creates a simple bipedal rig with:
    - Spine chain (hips, spine, chest, neck, head)
    - Arms (shoulder, upper arm, forearm, hand)
    - Legs (thigh, shin, foot)

    Automatically parents the armature to the selected mesh.
    """

    bl_idname = "blender_ai.auto_rig"
    bl_label = "Auto Rig"
    bl_description = "Create a basic armature rig"
    bl_options = {"REGISTER", "UNDO"}

    rig_type: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Rig Type",
        items=[
            ("BIPED", "Bipedal", "Human-like rig"),
            ("QUADRUPED", "Quadruped", "Four-legged rig"),
            ("SIMPLE_SPINE", "Simple Spine", "Basic spine chain only"),
        ],
        default="BIPED",
    )

    bone_size: bpy.props.FloatProperty = bpy.props.FloatProperty(
        name="Bone Size",
        default=1.0,
        min=0.1,
        max=10.0,
        description="Scale factor for the rig",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        target_obj = _get_target_object(context)

        # Create armature data
        armature_data = bpy.data.armatures.new(name="AI_Rig")
        armature_obj = bpy.data.objects.new(name="AI_Armature", object_data=armature_data)

        # Link to collection
        context.collection.objects.link(armature_obj)

        # Set as active and enter edit mode
        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode="EDIT")

        scale = self.bone_size

        if self.rig_type == "SIMPLE_SPINE":
            self._create_spine(armature_data, scale)
        elif self.rig_type == "QUADRUPED":
            self._create_quadruped(armature_data, scale)
        else:  # BIPED
            self._create_biped(armature_data, scale)

        # Exit edit mode
        bpy.ops.object.mode_set(mode="OBJECT")

        # Parent mesh to armature if target exists
        if target_obj:
            target_obj.select_set(True)
            armature_obj.select_set(True)
            context.view_layer.objects.active = armature_obj
            bpy.ops.object.parent_set(type="ARMATURE_AUTO")
            self.report({"INFO"}, f"Armatura creata e associata a '{target_obj.name}'")
        else:
            self.report({"INFO"}, "Armatura creata (nessun mesh selezionato per parenting)")

        return {"FINISHED"}

    def _create_spine(self, armature: bpy.types.Armature, scale: float) -> None:
        """Create a simple spine chain."""
        bones_data = [
            ("Hips", (0, 0, 1.0), (0, 0, 1.2)),
            ("Spine", (0, 0, 1.2), (0, 0, 1.5)),
            ("Chest", (0, 0, 1.5), (0, 0, 1.8)),
            ("Neck", (0, 0, 1.8), (0, 0, 1.95)),
            ("Head", (0, 0, 1.95), (0, 0, 2.2)),
        ]

        parent_bone = None
        for name, head, tail in bones_data:
            bone = armature.edit_bones.new(name)
            bone.head = (head[0] * scale, head[1] * scale, head[2] * scale)
            bone.tail = (tail[0] * scale, tail[1] * scale, tail[2] * scale)
            if parent_bone:
                bone.parent = parent_bone
                bone.use_connect = True
            parent_bone = bone

    def _create_biped(self, armature: bpy.types.Armature, scale: float) -> None:
        """Create a full biped rig."""
        # Spine
        self._create_spine(armature, scale)

        spine_bone = armature.edit_bones.get("Spine")
        chest_bone = armature.edit_bones.get("Chest")
        hips_bone = armature.edit_bones.get("Hips")

        # Arms (both sides)
        for side, x_mult in [("L", 1), ("R", -1)]:
            # Shoulder
            shoulder = armature.edit_bones.new(f"Shoulder.{side}")
            shoulder.head = (0.1 * x_mult * scale, 0, 1.7 * scale)
            shoulder.tail = (0.2 * x_mult * scale, 0, 1.7 * scale)
            shoulder.parent = chest_bone

            # Upper Arm
            upper_arm = armature.edit_bones.new(f"UpperArm.{side}")
            upper_arm.head = (0.2 * x_mult * scale, 0, 1.7 * scale)
            upper_arm.tail = (0.5 * x_mult * scale, 0, 1.4 * scale)
            upper_arm.parent = shoulder
            upper_arm.use_connect = True

            # Forearm
            forearm = armature.edit_bones.new(f"Forearm.{side}")
            forearm.head = (0.5 * x_mult * scale, 0, 1.4 * scale)
            forearm.tail = (0.8 * x_mult * scale, 0, 1.1 * scale)
            forearm.parent = upper_arm
            forearm.use_connect = True

            # Hand
            hand = armature.edit_bones.new(f"Hand.{side}")
            hand.head = (0.8 * x_mult * scale, 0, 1.1 * scale)
            hand.tail = (0.9 * x_mult * scale, 0, 1.0 * scale)
            hand.parent = forearm
            hand.use_connect = True

        # Legs (both sides)
        for side, x_mult in [("L", 1), ("R", -1)]:
            # Thigh
            thigh = armature.edit_bones.new(f"Thigh.{side}")
            thigh.head = (0.1 * x_mult * scale, 0, 1.0 * scale)
            thigh.tail = (0.1 * x_mult * scale, 0, 0.5 * scale)
            thigh.parent = hips_bone

            # Shin
            shin = armature.edit_bones.new(f"Shin.{side}")
            shin.head = (0.1 * x_mult * scale, 0, 0.5 * scale)
            shin.tail = (0.1 * x_mult * scale, 0, 0.1 * scale)
            shin.parent = thigh
            shin.use_connect = True

            # Foot
            foot = armature.edit_bones.new(f"Foot.{side}")
            foot.head = (0.1 * x_mult * scale, 0, 0.1 * scale)
            foot.tail = (0.1 * x_mult * scale, 0.15 * scale, 0)
            foot.parent = shin
            foot.use_connect = True

    def _create_quadruped(self, armature: bpy.types.Armature, scale: float) -> None:
        """Create a quadruped rig (e.g., for animals)."""
        # Spine (horizontal)
        spine_bones = [
            ("Hips", (0, -0.3, 0.8), (0, 0, 0.8)),
            ("Spine", (0, 0, 0.8), (0, 0.3, 0.85)),
            ("Chest", (0, 0.3, 0.85), (0, 0.6, 0.9)),
            ("Neck", (0, 0.6, 0.9), (0, 0.8, 1.1)),
            ("Head", (0, 0.8, 1.1), (0, 1.0, 1.15)),
        ]

        parent_bone = None
        for name, head, tail in spine_bones:
            bone = armature.edit_bones.new(name)
            bone.head = (head[0] * scale, head[1] * scale, head[2] * scale)
            bone.tail = (tail[0] * scale, tail[1] * scale, tail[2] * scale)
            if parent_bone:
                bone.parent = parent_bone
                bone.use_connect = True
            parent_bone = bone

        hips_bone = armature.edit_bones.get("Hips")
        chest_bone = armature.edit_bones.get("Chest")

        # Front legs
        for side, x_mult in [("L", 1), ("R", -1)]:
            upper = armature.edit_bones.new(f"FrontUpperLeg.{side}")
            upper.head = (0.15 * x_mult * scale, 0.5 * scale, 0.8 * scale)
            upper.tail = (0.15 * x_mult * scale, 0.5 * scale, 0.4 * scale)
            upper.parent = chest_bone

            lower = armature.edit_bones.new(f"FrontLowerLeg.{side}")
            lower.head = (0.15 * x_mult * scale, 0.5 * scale, 0.4 * scale)
            lower.tail = (0.15 * x_mult * scale, 0.5 * scale, 0.05 * scale)
            lower.parent = upper
            lower.use_connect = True

        # Back legs
        for side, x_mult in [("L", 1), ("R", -1)]:
            upper = armature.edit_bones.new(f"BackUpperLeg.{side}")
            upper.head = (0.15 * x_mult * scale, -0.3 * scale, 0.7 * scale)
            upper.tail = (0.15 * x_mult * scale, -0.3 * scale, 0.35 * scale)
            upper.parent = hips_bone

            lower = armature.edit_bones.new(f"BackLowerLeg.{side}")
            lower.head = (0.15 * x_mult * scale, -0.3 * scale, 0.35 * scale)
            lower.tail = (0.15 * x_mult * scale, -0.3 * scale, 0.05 * scale)
            lower.parent = upper
            lower.use_connect = True

        # Tail
        tail_base = armature.edit_bones.new("Tail.001")
        tail_base.head = (0, -0.3 * scale, 0.8 * scale)
        tail_base.tail = (0, -0.5 * scale, 0.75 * scale)
        tail_base.parent = hips_bone

        tail_mid = armature.edit_bones.new("Tail.002")
        tail_mid.head = (0, -0.5 * scale, 0.75 * scale)
        tail_mid.tail = (0, -0.7 * scale, 0.7 * scale)
        tail_mid.parent = tail_base
        tail_mid.use_connect = True


class BLENDER_AI_OT_auto_geometry(bpy.types.Operator):
    """Create procedural geometry using Geometry Nodes.

    Available patterns:
    - GRID: Array of objects in a grid pattern
    - SCATTER: Random scatter on surface
    - CIRCULAR: Circular array
    - SPIRAL: Spiral pattern
    - WAVE: Deformation wave effect
    """

    bl_idname = "blender_ai.auto_geometry"
    bl_label = "Auto Geometry"
    bl_description = "Create procedural geometry with Geometry Nodes"
    bl_options = {"REGISTER", "UNDO"}

    pattern: bpy.props.EnumProperty = bpy.props.EnumProperty(
        name="Pattern",
        items=[
            ("GRID", "Grid Array", "Create a grid of instances"),
            ("SCATTER", "Surface Scatter", "Scatter points on surface"),
            ("CIRCULAR", "Circular Array", "Arrange in a circle"),
            ("SPIRAL", "Spiral", "Spiral arrangement"),
            ("WAVE", "Wave Deform", "Wave deformation effect"),
        ],
        default="GRID",
    )

    count_x: bpy.props.IntProperty = bpy.props.IntProperty(
        name="Count X",
        default=5,
        min=1,
        max=100,
        description="Number of instances in X direction",
    )

    count_y: bpy.props.IntProperty = bpy.props.IntProperty(
        name="Count Y",
        default=5,
        min=1,
        max=100,
        description="Number of instances in Y direction",
    )

    spacing: bpy.props.FloatProperty = bpy.props.FloatProperty(
        name="Spacing",
        default=1.5,
        min=0.1,
        max=10.0,
        description="Distance between instances",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        obj = _get_target_object(context)

        if self.pattern == "GRID":
            self._create_grid_geometry(context, obj)
        elif self.pattern == "SCATTER":
            self._create_scatter_geometry(context, obj)
        elif self.pattern == "CIRCULAR":
            self._create_circular_geometry(context, obj)
        elif self.pattern == "SPIRAL":
            self._create_spiral_geometry(context, obj)
        elif self.pattern == "WAVE":
            self._create_wave_geometry(context, obj)

        return {"FINISHED"}

    def _create_grid_geometry(self, context: bpy.types.Context, source_obj: Optional[bpy.types.Object]) -> None:
        """Create a grid array using Geometry Nodes."""
        # Create a plane as base
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        base_obj = context.active_object
        base_obj.name = "AI_Grid_Base"

        # Create geometry nodes modifier
        modifier = base_obj.modifiers.new(name="AI_Grid_Nodes", type="NODES")

        # Create node group
        node_group = bpy.data.node_groups.new(name="AI_Grid_Setup", type="GeometryNodeTree")
        modifier.node_group = node_group

        # Create nodes
        nodes = node_group.nodes
        links = node_group.links

        # Input/Output
        input_node = nodes.new("NodeGroupInput")
        input_node.location = (-400, 0)

        output_node = nodes.new("NodeGroupOutput")
        output_node.location = (400, 0)

        # Create interface sockets
        node_group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

        # Grid node
        grid_node = nodes.new("GeometryNodeMeshGrid")
        grid_node.location = (-200, 0)
        grid_node.inputs["Size X"].default_value = self.count_x * self.spacing
        grid_node.inputs["Size Y"].default_value = self.count_y * self.spacing
        grid_node.inputs["Vertices X"].default_value = self.count_x
        grid_node.inputs["Vertices Y"].default_value = self.count_y

        # Instance on points
        if source_obj:
            instance_node = nodes.new("GeometryNodeInstanceOnPoints")
            instance_node.location = (0, 0)

            object_info = nodes.new("GeometryNodeObjectInfo")
            object_info.location = (-200, -150)
            object_info.inputs["Object"].default_value = source_obj

            links.new(grid_node.outputs["Mesh"], instance_node.inputs["Points"])
            links.new(object_info.outputs["Geometry"], instance_node.inputs["Instance"])
            links.new(instance_node.outputs["Instances"], output_node.inputs["Geometry"])
        else:
            # Just output the grid
            links.new(grid_node.outputs["Mesh"], output_node.inputs["Geometry"])

        self.report({"INFO"}, f"Grid {self.count_x}x{self.count_y} creata con Geometry Nodes")

    def _create_scatter_geometry(self, context: bpy.types.Context, source_obj: Optional[bpy.types.Object]) -> None:
        """Create scatter points on a surface."""
        obj = _get_target_object(context)
        if not obj:
            bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))
            obj = context.active_object
            obj.name = "AI_Scatter_Surface"

        modifier = obj.modifiers.new(name="AI_Scatter_Nodes", type="NODES")
        node_group = bpy.data.node_groups.new(name="AI_Scatter_Setup", type="GeometryNodeTree")
        modifier.node_group = node_group

        nodes = node_group.nodes
        links = node_group.links

        input_node = nodes.new("NodeGroupInput")
        input_node.location = (-400, 0)

        output_node = nodes.new("NodeGroupOutput")
        output_node.location = (400, 0)

        node_group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

        # Distribute points
        distribute = nodes.new("GeometryNodeDistributePointsOnFaces")
        distribute.location = (-100, 0)
        distribute.inputs["Density"].default_value = float(self.count_x * self.count_y) / 10.0

        links.new(input_node.outputs["Geometry"], distribute.inputs["Mesh"])

        if source_obj:
            instance_node = nodes.new("GeometryNodeInstanceOnPoints")
            instance_node.location = (100, 0)

            object_info = nodes.new("GeometryNodeObjectInfo")
            object_info.location = (-100, -150)
            object_info.inputs["Object"].default_value = source_obj

            # Random scale
            random_val = nodes.new("FunctionNodeRandomValue")
            random_val.location = (-100, -300)
            random_val.data_type = "FLOAT"
            random_val.inputs[2].default_value = 0.5  # Min
            random_val.inputs[3].default_value = 1.5  # Max

            links.new(distribute.outputs["Points"], instance_node.inputs["Points"])
            links.new(object_info.outputs["Geometry"], instance_node.inputs["Instance"])
            links.new(random_val.outputs[1], instance_node.inputs["Scale"])

            # Join with original
            join = nodes.new("GeometryNodeJoinGeometry")
            join.location = (250, 0)
            links.new(input_node.outputs["Geometry"], join.inputs["Geometry"])
            links.new(instance_node.outputs["Instances"], join.inputs["Geometry"])
            links.new(join.outputs["Geometry"], output_node.inputs["Geometry"])
        else:
            # Mesh to points
            mesh_to_points = nodes.new("GeometryNodeMeshToPoints")
            mesh_to_points.location = (100, 0)
            links.new(distribute.outputs["Points"], mesh_to_points.inputs["Mesh"])
            links.new(mesh_to_points.outputs["Points"], output_node.inputs["Geometry"])

        self.report({"INFO"}, "Scatter distribution creata con Geometry Nodes")

    def _create_circular_geometry(self, context: bpy.types.Context, source_obj: Optional[bpy.types.Object]) -> None:
        """Create circular array."""
        bpy.ops.mesh.primitive_circle_add(vertices=self.count_x, radius=self.spacing * self.count_x / (2 * math.pi))
        base_obj = context.active_object
        base_obj.name = "AI_Circular_Base"

        if source_obj:
            modifier = base_obj.modifiers.new(name="AI_Circular_Nodes", type="NODES")
            node_group = bpy.data.node_groups.new(name="AI_Circular_Setup", type="GeometryNodeTree")
            modifier.node_group = node_group

            nodes = node_group.nodes
            links = node_group.links

            input_node = nodes.new("NodeGroupInput")
            input_node.location = (-400, 0)
            output_node = nodes.new("NodeGroupOutput")
            output_node.location = (400, 0)

            node_group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
            node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

            # Mesh to points
            to_points = nodes.new("GeometryNodeMeshToPoints")
            to_points.location = (-200, 0)

            # Instance on points
            instance = nodes.new("GeometryNodeInstanceOnPoints")
            instance.location = (0, 0)

            object_info = nodes.new("GeometryNodeObjectInfo")
            object_info.location = (-200, -150)
            object_info.inputs["Object"].default_value = source_obj

            links.new(input_node.outputs["Geometry"], to_points.inputs["Mesh"])
            links.new(to_points.outputs["Points"], instance.inputs["Points"])
            links.new(object_info.outputs["Geometry"], instance.inputs["Instance"])
            links.new(instance.outputs["Instances"], output_node.inputs["Geometry"])

        self.report({"INFO"}, f"Array circolare con {self.count_x} elementi creato")

    def _create_spiral_geometry(self, context: bpy.types.Context, source_obj: Optional[bpy.types.Object]) -> None:
        """Create spiral pattern."""
        # Create curve spiral
        bpy.ops.curve.primitive_bezier_circle_add(radius=1)
        curve = context.active_object
        curve.name = "AI_Spiral_Curve"

        # Add screw modifier for spiral effect
        screw = curve.modifiers.new(name="Spiral", type="SCREW")
        screw.steps = self.count_x * 2
        screw.render_steps = self.count_x * 2
        screw.screw_offset = self.spacing * self.count_x
        screw.iterations = max(1, self.count_y // 2)

        # Convert to mesh
        bpy.ops.object.convert(target="MESH")

        self.report({"INFO"}, "Spirale creata")

    def _create_wave_geometry(self, context: bpy.types.Context, source_obj: Optional[bpy.types.Object]) -> None:
        """Create wave deformation."""
        obj = _get_target_object(context)
        if not obj:
            bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))
            obj = context.active_object
            obj.name = "AI_Wave_Surface"
            # Subdivide for better deformation
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.subdivide(number_cuts=20)
            bpy.ops.object.mode_set(mode="OBJECT")

        # Add wave modifier
        wave = obj.modifiers.new(name="AI_Wave", type="WAVE")
        wave.use_normal = True
        wave.height = self.spacing * 0.5
        wave.width = self.spacing * 2
        wave.speed = 1.0
        wave.time_offset = 0

        self.report({"INFO"}, "Deformazione Wave applicata")


# =============================================================================
# CLASS REGISTRATION
# =============================================================================

classes = (
    BLENDER_AI_OT_generate_suggestions,
    BLENDER_AI_OT_analyze_scene,
    BLENDER_AI_OT_preview_code,
    BLENDER_AI_OT_apply_preview,
    BLENDER_AI_OT_auto_material,
    BLENDER_AI_OT_auto_light,
    BLENDER_AI_OT_auto_rig,
    BLENDER_AI_OT_auto_geometry,
)
