"""AI Agent Controller - Full control over Blender via natural language.

This is the core AI agent that can:
- Interpret natural language commands
- Execute any Blender operation
- Create/modify objects, materials, lights
- Control render settings
- Manage scene hierarchy
- Generate and execute Python code

Uses Gemini API for natural language understanding.
"""

from __future__ import annotations

import json
import re
import traceback
from typing import Any, Dict, List, Optional, Tuple

import bpy

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


# =============================================================================
# BLENDER COMMAND DEFINITIONS
# =============================================================================

BLENDER_COMMANDS = {
    # Object Creation
    "create_cube": {
        "description": "Create a cube mesh",
        "params": {"size": "float", "location": "tuple(x,y,z)", "name": "string"},
        "code": "bpy.ops.mesh.primitive_cube_add(size={size}, location={location}); bpy.context.active_object.name = '{name}'"
    },
    "create_sphere": {
        "description": "Create a UV sphere",
        "params": {"radius": "float", "location": "tuple(x,y,z)", "segments": "int"},
        "code": "bpy.ops.mesh.primitive_uv_sphere_add(radius={radius}, location={location}, segments={segments})"
    },
    "create_cylinder": {
        "description": "Create a cylinder",
        "params": {"radius": "float", "depth": "float", "location": "tuple(x,y,z)"},
        "code": "bpy.ops.mesh.primitive_cylinder_add(radius={radius}, depth={depth}, location={location})"
    },
    "create_plane": {
        "description": "Create a plane",
        "params": {"size": "float", "location": "tuple(x,y,z)"},
        "code": "bpy.ops.mesh.primitive_plane_add(size={size}, location={location})"
    },
    "create_torus": {
        "description": "Create a torus/donut",
        "params": {"major_radius": "float", "minor_radius": "float", "location": "tuple(x,y,z)"},
        "code": "bpy.ops.mesh.primitive_torus_add(major_radius={major_radius}, minor_radius={minor_radius}, location={location})"
    },
    "create_cone": {
        "description": "Create a cone",
        "params": {"radius1": "float", "depth": "float", "location": "tuple(x,y,z)"},
        "code": "bpy.ops.mesh.primitive_cone_add(radius1={radius1}, depth={depth}, location={location})"
    },
    "create_monkey": {
        "description": "Create Suzanne monkey head",
        "params": {"location": "tuple(x,y,z)"},
        "code": "bpy.ops.mesh.primitive_monkey_add(location={location})"
    },
    "create_text": {
        "description": "Create 3D text",
        "params": {"text": "string", "location": "tuple(x,y,z)"},
        "code": "bpy.ops.object.text_add(location={location}); bpy.context.active_object.data.body = '{text}'"
    },
    "create_empty": {
        "description": "Create an empty object",
        "params": {"type": "string", "location": "tuple(x,y,z)"},
        "code": "bpy.ops.object.empty_add(type='{type}', location={location})"
    },
    "create_camera": {
        "description": "Create a camera",
        "params": {"location": "tuple(x,y,z)", "rotation": "tuple(x,y,z)"},
        "code": "bpy.ops.object.camera_add(location={location}, rotation={rotation})"
    },
    "create_light": {
        "description": "Create a light",
        "params": {"type": "string", "location": "tuple(x,y,z)", "energy": "float"},
        "code": "bpy.ops.object.light_add(type='{type}', location={location}); bpy.context.active_object.data.energy = {energy}"
    },

    # Object Manipulation
    "select_object": {
        "description": "Select an object by name",
        "params": {"name": "string"},
        "code": "bpy.ops.object.select_all(action='DESELECT'); bpy.data.objects['{name}'].select_set(True); bpy.context.view_layer.objects.active = bpy.data.objects['{name}']"
    },
    "delete_object": {
        "description": "Delete selected object or by name",
        "params": {"name": "string"},
        "code": "bpy.data.objects.remove(bpy.data.objects['{name}'], do_unlink=True)"
    },
    "duplicate_object": {
        "description": "Duplicate selected object",
        "params": {},
        "code": "bpy.ops.object.duplicate()"
    },
    "move_object": {
        "description": "Move object to location",
        "params": {"name": "string", "location": "tuple(x,y,z)"},
        "code": "bpy.data.objects['{name}'].location = {location}"
    },
    "rotate_object": {
        "description": "Rotate object (in radians)",
        "params": {"name": "string", "rotation": "tuple(x,y,z)"},
        "code": "bpy.data.objects['{name}'].rotation_euler = {rotation}"
    },
    "scale_object": {
        "description": "Scale object",
        "params": {"name": "string", "scale": "tuple(x,y,z)"},
        "code": "bpy.data.objects['{name}'].scale = {scale}"
    },
    "rename_object": {
        "description": "Rename object",
        "params": {"old_name": "string", "new_name": "string"},
        "code": "bpy.data.objects['{old_name}'].name = '{new_name}'"
    },
    "hide_object": {
        "description": "Hide object",
        "params": {"name": "string"},
        "code": "bpy.data.objects['{name}'].hide_set(True)"
    },
    "show_object": {
        "description": "Show hidden object",
        "params": {"name": "string"},
        "code": "bpy.data.objects['{name}'].hide_set(False)"
    },

    # Materials
    "create_material": {
        "description": "Create a new material",
        "params": {"name": "string", "color": "tuple(r,g,b,a)"},
        "code": "mat = bpy.data.materials.new(name='{name}'); mat.use_nodes = True; mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = {color}"
    },
    "assign_material": {
        "description": "Assign material to object",
        "params": {"object_name": "string", "material_name": "string"},
        "code": "obj = bpy.data.objects['{object_name}']; mat = bpy.data.materials['{material_name}']; obj.data.materials.clear(); obj.data.materials.append(mat)"
    },
    "set_material_property": {
        "description": "Set material property",
        "params": {"material_name": "string", "property": "string", "value": "any"},
        "code": "bpy.data.materials['{material_name}'].node_tree.nodes['Principled BSDF'].inputs['{property}'].default_value = {value}"
    },

    # Modifiers
    "add_modifier": {
        "description": "Add modifier to object",
        "params": {"object_name": "string", "modifier_type": "string"},
        "code": "bpy.data.objects['{object_name}'].modifiers.new(name='{modifier_type}', type='{modifier_type}')"
    },
    "add_subdivision": {
        "description": "Add subdivision modifier",
        "params": {"object_name": "string", "levels": "int"},
        "code": "mod = bpy.data.objects['{object_name}'].modifiers.new(name='Subdivision', type='SUBSURF'); mod.levels = {levels}"
    },
    "add_bevel": {
        "description": "Add bevel modifier",
        "params": {"object_name": "string", "width": "float"},
        "code": "mod = bpy.data.objects['{object_name}'].modifiers.new(name='Bevel', type='BEVEL'); mod.width = {width}"
    },
    "add_mirror": {
        "description": "Add mirror modifier",
        "params": {"object_name": "string", "axis": "string"},
        "code": "mod = bpy.data.objects['{object_name}'].modifiers.new(name='Mirror', type='MIRROR')"
    },
    "apply_modifier": {
        "description": "Apply modifier",
        "params": {"object_name": "string", "modifier_name": "string"},
        "code": "bpy.context.view_layer.objects.active = bpy.data.objects['{object_name}']; bpy.ops.object.modifier_apply(modifier='{modifier_name}')"
    },

    # Scene
    "set_render_engine": {
        "description": "Set render engine (CYCLES, BLENDER_EEVEE_NEXT)",
        "params": {"engine": "string"},
        "code": "bpy.context.scene.render.engine = '{engine}'"
    },
    "set_render_resolution": {
        "description": "Set render resolution",
        "params": {"x": "int", "y": "int"},
        "code": "bpy.context.scene.render.resolution_x = {x}; bpy.context.scene.render.resolution_y = {y}"
    },
    "set_render_samples": {
        "description": "Set render samples",
        "params": {"samples": "int"},
        "code": "bpy.context.scene.cycles.samples = {samples}"
    },
    "render_image": {
        "description": "Render current frame",
        "params": {},
        "code": "bpy.ops.render.render()"
    },
    "save_render": {
        "description": "Save rendered image",
        "params": {"filepath": "string"},
        "code": "bpy.context.scene.render.filepath = '{filepath}'; bpy.ops.render.render(write_still=True)"
    },
    "set_frame": {
        "description": "Set current frame",
        "params": {"frame": "int"},
        "code": "bpy.context.scene.frame_set({frame})"
    },
    "set_frame_range": {
        "description": "Set animation frame range",
        "params": {"start": "int", "end": "int"},
        "code": "bpy.context.scene.frame_start = {start}; bpy.context.scene.frame_end = {end}"
    },

    # Animation
    "insert_keyframe": {
        "description": "Insert keyframe on object",
        "params": {"object_name": "string", "data_path": "string", "frame": "int"},
        "code": "bpy.data.objects['{object_name}'].keyframe_insert(data_path='{data_path}', frame={frame})"
    },
    "clear_keyframes": {
        "description": "Clear all keyframes from object",
        "params": {"object_name": "string"},
        "code": "bpy.data.objects['{object_name}'].animation_data_clear()"
    },

    # Edit Mode
    "enter_edit_mode": {
        "description": "Enter edit mode",
        "params": {},
        "code": "bpy.ops.object.mode_set(mode='EDIT')"
    },
    "exit_edit_mode": {
        "description": "Exit edit mode to object mode",
        "params": {},
        "code": "bpy.ops.object.mode_set(mode='OBJECT')"
    },
    "select_all_vertices": {
        "description": "Select all vertices in edit mode",
        "params": {},
        "code": "bpy.ops.mesh.select_all(action='SELECT')"
    },
    "extrude": {
        "description": "Extrude selected geometry",
        "params": {"value": "tuple(x,y,z)"},
        "code": "bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={'value': {value}})"
    },
    "subdivide": {
        "description": "Subdivide selected faces",
        "params": {"cuts": "int"},
        "code": "bpy.ops.mesh.subdivide(number_cuts={cuts})"
    },
    "bevel_vertices": {
        "description": "Bevel vertices/edges",
        "params": {"offset": "float"},
        "code": "bpy.ops.mesh.bevel(offset={offset})"
    },
    "loop_cut": {
        "description": "Add loop cut",
        "params": {"cuts": "int"},
        "code": "bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={{'number_cuts': {cuts}}})"
    },

    # Collections
    "create_collection": {
        "description": "Create new collection",
        "params": {"name": "string"},
        "code": "col = bpy.data.collections.new('{name}'); bpy.context.scene.collection.children.link(col)"
    },
    "move_to_collection": {
        "description": "Move object to collection",
        "params": {"object_name": "string", "collection_name": "string"},
        "code": "obj = bpy.data.objects['{object_name}']; col = bpy.data.collections['{collection_name}']; col.objects.link(obj)"
    },

    # Viewport
    "set_viewport_shading": {
        "description": "Set viewport shading mode",
        "params": {"type": "string"},
        "code": "bpy.context.space_data.shading.type = '{type}'"
    },
    "frame_selected": {
        "description": "Frame selected objects in view",
        "params": {},
        "code": "bpy.ops.view3d.view_selected()"
    },
    "view_camera": {
        "description": "Switch to camera view",
        "params": {},
        "code": "bpy.ops.view3d.view_camera()"
    },

    # File operations
    "save_file": {
        "description": "Save current file",
        "params": {},
        "code": "bpy.ops.wm.save_mainfile()"
    },
    "save_as": {
        "description": "Save file as",
        "params": {"filepath": "string"},
        "code": "bpy.ops.wm.save_as_mainfile(filepath='{filepath}')"
    },
    "export_fbx": {
        "description": "Export as FBX",
        "params": {"filepath": "string"},
        "code": "bpy.ops.export_scene.fbx(filepath='{filepath}')"
    },
    "export_obj": {
        "description": "Export as OBJ",
        "params": {"filepath": "string"},
        "code": "bpy.ops.wm.obj_export(filepath='{filepath}')"
    },
    "export_gltf": {
        "description": "Export as glTF",
        "params": {"filepath": "string"},
        "code": "bpy.ops.export_scene.gltf(filepath='{filepath}')"
    },
}


# =============================================================================
# AI AGENT CONTROLLER
# =============================================================================

class AIAgentController:
    """Main AI agent that interprets commands and controls Blender."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """Initialize the AI agent.

        Args:
            api_key: Gemini API key
            model: Model to use (gemini-2.0-flash, gemini-1.5-pro, etc.)
        """
        self.api_key = api_key
        self.model_name = model
        self.model = None
        self.chat = None
        self.command_history: List[Dict[str, Any]] = []

        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model)
                self.chat = self.model.start_chat(history=[])
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")

    def _get_scene_context(self) -> str:
        """Get current scene context for AI."""
        context_parts = []

        # Objects
        objects = []
        for obj in bpy.data.objects:
            obj_info = {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "visible": obj.visible_get(),
            }
            if obj.type == "MESH":
                obj_info["vertices"] = len(obj.data.vertices)
                obj_info["materials"] = [m.name for m in obj.data.materials if m]
            objects.append(obj_info)
        context_parts.append(f"Objects in scene: {json.dumps(objects, indent=2)}")

        # Materials
        materials = [m.name for m in bpy.data.materials]
        context_parts.append(f"Materials: {materials}")

        # Render settings
        render = {
            "engine": bpy.context.scene.render.engine,
            "resolution": f"{bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}",
            "frame_range": f"{bpy.context.scene.frame_start}-{bpy.context.scene.frame_end}",
        }
        context_parts.append(f"Render settings: {json.dumps(render)}")

        # Active object
        if bpy.context.active_object:
            context_parts.append(f"Active object: {bpy.context.active_object.name}")

        # Selected objects
        selected = [obj.name for obj in bpy.context.selected_objects]
        if selected:
            context_parts.append(f"Selected objects: {selected}")

        return "\n".join(context_parts)

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI."""
        commands_desc = "\n".join([
            f"- {name}: {cmd['description']} (params: {cmd['params']})"
            for name, cmd in BLENDER_COMMANDS.items()
        ])

        return f"""You are an AI assistant that controls Blender 3D software.
You can execute commands to create, modify, and manage 3D objects, materials, lights, and scenes.

AVAILABLE COMMANDS:
{commands_desc}

RESPONSE FORMAT:
Always respond with a JSON object containing:
{{
    "thinking": "Your reasoning about what the user wants",
    "commands": [
        {{"command": "command_name", "params": {{"param1": value1, ...}}}},
        ...
    ],
    "explanation": "Brief explanation of what you did",
    "python_code": "Optional: raw Python code if commands aren't sufficient"
}}

IMPORTANT RULES:
1. Use radians for rotation (import math for conversions)
2. Colors are RGBA tuples (0.0-1.0 range)
3. Locations are (x, y, z) tuples
4. Always validate object names exist before operating on them
5. If the user's request isn't clear, ask for clarification
6. For complex operations not covered by commands, provide python_code
7. Be creative and helpful - interpret user intent

CURRENT SCENE STATE:
{self._get_scene_context()}
"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured commands."""
        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Fallback: treat as explanation only
        return {
            "thinking": "",
            "commands": [],
            "explanation": response_text,
            "python_code": ""
        }

    def _execute_command(self, command_name: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Execute a single Blender command.

        Returns:
            Tuple of (success, message)
        """
        if command_name not in BLENDER_COMMANDS:
            return False, f"Unknown command: {command_name}"

        cmd = BLENDER_COMMANDS[command_name]
        code_template = cmd["code"]

        try:
            # Format code with parameters
            code = code_template.format(**params)

            # Execute
            exec(code, {"bpy": bpy, "math": __import__("math")})

            return True, f"Executed: {command_name}"
        except KeyError as e:
            return False, f"Missing parameter: {e}"
        except Exception as e:
            return False, f"Error executing {command_name}: {e}"

    def _execute_python_code(self, code: str) -> Tuple[bool, str]:
        """Execute raw Python code safely.

        Returns:
            Tuple of (success, message)
        """
        # Safety checks
        dangerous = ["os.system", "subprocess", "__import__", "eval", "exec"]
        for pattern in dangerous:
            if pattern in code:
                return False, f"Blocked dangerous pattern: {pattern}"

        try:
            exec(code, {
                "bpy": bpy,
                "math": __import__("math"),
                "Vector": None,
                "Matrix": None,
            })
            return True, "Python code executed"
        except Exception as e:
            return False, f"Python error: {e}"

    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process a natural language command.

        Args:
            user_input: Natural language command from user

        Returns:
            Dict with results and execution status
        """
        result = {
            "success": False,
            "input": user_input,
            "thinking": "",
            "commands_executed": [],
            "explanation": "",
            "errors": [],
        }

        if not self.model:
            result["errors"].append("AI model not initialized. Check API key.")
            return result

        try:
            # Build prompt with context
            system_prompt = self._build_system_prompt()
            full_prompt = f"{system_prompt}\n\nUSER REQUEST: {user_input}"

            # Get AI response
            response = self.chat.send_message(full_prompt)
            response_text = response.text

            # Parse response
            parsed = self._parse_response(response_text)
            result["thinking"] = parsed.get("thinking", "")
            result["explanation"] = parsed.get("explanation", "")

            # Execute commands
            for cmd_info in parsed.get("commands", []):
                cmd_name = cmd_info.get("command")
                cmd_params = cmd_info.get("params", {})

                success, message = self._execute_command(cmd_name, cmd_params)

                result["commands_executed"].append({
                    "command": cmd_name,
                    "params": cmd_params,
                    "success": success,
                    "message": message,
                })

                if not success:
                    result["errors"].append(message)

            # Execute raw Python if provided
            python_code = parsed.get("python_code", "")
            if python_code and python_code.strip():
                success, message = self._execute_python_code(python_code)
                result["commands_executed"].append({
                    "command": "python_code",
                    "success": success,
                    "message": message,
                })
                if not success:
                    result["errors"].append(message)

            result["success"] = len(result["errors"]) == 0

            # Store in history
            self.command_history.append(result)

        except Exception as e:
            result["errors"].append(f"AI processing error: {str(e)}")
            traceback.print_exc()

        return result


# =============================================================================
# GLOBAL AGENT INSTANCE
# =============================================================================

_agent_instance: Optional[AIAgentController] = None


def get_agent(api_key: Optional[str] = None) -> Optional[AIAgentController]:
    """Get or create the global AI agent instance."""
    global _agent_instance

    if api_key:
        _agent_instance = AIAgentController(api_key)

    return _agent_instance


def process_natural_language(command: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Process a natural language command.

    Args:
        command: Natural language command
        api_key: Optional API key (uses cached if not provided)

    Returns:
        Execution result dict
    """
    agent = get_agent(api_key)
    if not agent:
        return {"success": False, "errors": ["Agent not initialized"]}

    return agent.process_command(command)


# =============================================================================
# BLENDER OPERATORS
# =============================================================================

class BLENDER_AI_OT_agent_command(bpy.types.Operator):
    """Execute AI agent command from natural language."""

    bl_idname = "blender_ai.agent_command"
    bl_label = "AI Command"
    bl_description = "Execute natural language command via AI"
    bl_options = {"REGISTER", "UNDO"}

    command: bpy.props.StringProperty = bpy.props.StringProperty(
        name="Command",
        default="",
        description="Natural language command",
    )

    def execute(self, context: bpy.types.Context) -> set[str]:
        scene = context.scene

        if not self.command:
            self.command = scene.ai_agent_command

        if not self.command:
            self.report({"WARNING"}, "No command provided")
            return {"CANCELLED"}

        # Get API key from scene or environment
        api_key = getattr(scene, "ai_agent_api_key", "") or "AIzaSyCmFGwGrKL_Cgcm7qpuE3bg06UZY-qZxws"

        if not api_key:
            self.report({"ERROR"}, "No API key configured")
            return {"CANCELLED"}

        # Process command
        result = process_natural_language(self.command, api_key)

        # Store result
        scene.ai_agent_last_result = json.dumps(result, indent=2, default=str)
        scene.ai_agent_last_explanation = result.get("explanation", "")

        if result["success"]:
            executed = len(result.get("commands_executed", []))
            self.report({"INFO"}, f"AI executed {executed} commands: {result.get('explanation', '')[:100]}")
            return {"FINISHED"}
        else:
            errors = "; ".join(result.get("errors", ["Unknown error"]))
            self.report({"ERROR"}, f"AI error: {errors[:200]}")
            return {"CANCELLED"}


class BLENDER_AI_PT_agent_panel(bpy.types.Panel):
    """Panel for AI Agent Controller."""

    bl_label = "AI Agent"
    bl_idname = "BLENDER_AI_PT_agent_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        scene = context.scene

        # API Key (collapsed)
        box = layout.box()
        box.label(text="AI Configuration", icon="SETTINGS")
        box.prop(scene, "ai_agent_api_key", text="API Key")

        # Command input
        box = layout.box()
        box.label(text="Natural Language Command", icon="CONSOLE")
        box.prop(scene, "ai_agent_command", text="")
        box.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Execute Command", icon="PLAY")

        # Quick commands
        box = layout.box()
        box.label(text="Quick Commands", icon="PRESET")

        col = box.column(align=True)

        # Row 1: Create objects
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Add Cube")
        op.command = "Create a cube at the origin"
        op = row.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Add Sphere")
        op.command = "Create a sphere at location (2, 0, 0)"

        # Row 2: Materials
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Gold Material")
        op.command = "Create a gold metallic material and apply it to the selected object"
        op = row.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Glass Material")
        op.command = "Make the selected object look like glass"

        # Row 3: Scene
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Add Lights")
        op.command = "Add a 3-point lighting setup for the scene"
        op = row.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Setup Render")
        op.command = "Setup cycles render at 1920x1080 with 128 samples"

        # Row 4: Complex
        row = col.row(align=True)
        op = row.operator(BLENDER_AI_OT_agent_command.bl_idname, text="Product Scene")
        op.command = "Create a product visualization scene with a plane, camera, and studio lighting"

        # Last result
        if hasattr(scene, "ai_agent_last_explanation") and scene.ai_agent_last_explanation:
            box = layout.box()
            box.label(text="Last Result", icon="INFO")
            col = box.column()
            # Wrap text
            for line in scene.ai_agent_last_explanation[:300].split(". "):
                if line.strip():
                    col.label(text=line.strip()[:60])


def register_properties():
    """Register scene properties for AI agent."""
    bpy.types.Scene.ai_agent_api_key = bpy.props.StringProperty(
        name="AI API Key",
        description="Gemini API key for AI agent",
        default="AIzaSyCmFGwGrKL_Cgcm7qpuE3bg06UZY-qZxws",
        subtype="PASSWORD",
    )
    bpy.types.Scene.ai_agent_command = bpy.props.StringProperty(
        name="AI Command",
        description="Natural language command for AI",
        default="",
    )
    bpy.types.Scene.ai_agent_last_result = bpy.props.StringProperty(
        name="Last Result",
        description="JSON result of last command",
        default="",
    )
    bpy.types.Scene.ai_agent_last_explanation = bpy.props.StringProperty(
        name="Last Explanation",
        description="Explanation from AI",
        default="",
    )


def unregister_properties():
    """Unregister scene properties."""
    del bpy.types.Scene.ai_agent_api_key
    del bpy.types.Scene.ai_agent_command
    del bpy.types.Scene.ai_agent_last_result
    del bpy.types.Scene.ai_agent_last_explanation


classes = (
    BLENDER_AI_OT_agent_command,
    BLENDER_AI_PT_agent_panel,
)
