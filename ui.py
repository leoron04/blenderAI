import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, EnumProperty, BoolProperty

# UI Panel - Beautiful, Simple, Powerful
class BLENDER_AI_PT_main_panel(Panel):
    """Main BlenderAI Control Panel"""
    bl_label = "🤖 BlenderAI Agent"
    bl_idname = "BLENDER_AI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BlenderAI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Main Title Box
        box = layout.box()
        row = box.row(align=True)
        row.label(text="AI Agent Configuration", icon='SETTINGS')
        
        # Model Selection
        box = layout.box()
        box.label(text="AI Model", icon='OUTLINER_DATA_EMPTY')
        box.prop(scene, "ai_model", text="")
        
        # API Key Input
        box = layout.box()
        box.label(text="API Key", icon='KEY_HLT')
        box.prop(scene, "ai_api_key", text="")
        
        # Scene Info Button
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("wm.blender_ai_analyze", text="Analyze Scene", icon='ZOOM_ALL')
        
        # Separator
        layout.separator()
        
        # Quick Actions
        box = layout.box()
        box.label(text="Quick Actions", icon='LIGHTPROBE_GRID')
        
        col = box.column(align=True)
        col.scale_y = 1.1
        col.operator("wm.blender_ai_agent", text="Ask Agent", icon='COMMENT')
        col.operator("wm.blender_ai_create_object", text="Create from AI", icon='ADD')
        col.operator("wm.blender_ai_apply_material", text="Generate Material", icon='SHADING_RENDERED')
        
        # Separator
        layout.separator()
        
        # Scene Statistics
        box = layout.box()
        box.label(text="Scene Info", icon='INFO')
        
        row = box.row()
        row.label(text=f"Objects: {len(context.scene.objects)}")
        row.label(text=f"Materials: {len(bpy.data.materials)}")
        
        # Help & Documentation
        layout.separator()
        box = layout.box()
        box.operator("wm.blender_ai_help", text="Help & Documentation", icon='QUESTION')


class BLENDER_AI_PT_settings_panel(Panel):
    """Advanced Settings Panel"""
    bl_label = "⚙️ Advanced Settings"
    bl_idname = "BLENDER_AI_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BlenderAI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Temperature Setting
        box = layout.box()
        box.label(text="AI Parameters", icon='MOD_ARRAY')
        box.prop(scene, "ai_temperature", text="Temperature", slider=True)
        box.prop(scene, "ai_max_tokens", text="Max Tokens")
        
        # Debug Mode
        box = layout.box()
        box.label(text="Debug", icon='CONSOLE')
        box.prop(scene, "ai_debug_mode", text="Enable Debug Mode")
        
        if scene.ai_debug_mode:
            box.label(text="Debug Output:", icon='OUTPUT')
            row = box.row()
            row.operator("wm.blender_ai_show_log", text="Show Log", icon='TEXT')


class BLENDER_AI_OT_analyze(Operator):
    """Analyze Blender Scene"""
    bl_idname = "wm.blender_ai_analyze"
    bl_label = "Analyze Scene"
    bl_description = "Analyze entire Blender scene"

    def execute(self, context):
        scene = context.scene
        objects_count = len(scene.objects)
        materials_count = len(bpy.data.materials)
        
        msg = f"Scene analyzed:\n- Objects: {objects_count}\n- Materials: {materials_count}"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class BLENDER_AI_OT_help(Operator):
    """Show Help"""
    bl_idname = "wm.blender_ai_help"
    bl_label = "Help"

    def execute(self, context):
        self.report({'INFO'}, "Visit: https://github.com/leoron04/blenderAI")
        return {'FINISHED'}


class BLENDER_AI_OT_show_log(Operator):
    """Show Debug Log"""
    bl_idname = "wm.blender_ai_show_log"
    bl_label = "Show Log"

    def execute(self, context):
        self.report({'INFO'}, "Debug log loaded")
        return {'FINISHED'}


class BLENDER_AI_OT_create_object(Operator):
    """Create object from AI"""
    bl_idname = "wm.blender_ai_create_object"
    bl_label = "Create from AI"

    def execute(self, context):
        self.report({'INFO'}, "Object creation initiated")
        return {'FINISHED'}


class BLENDER_AI_OT_apply_material(Operator):
    """Generate material using AI"""
    bl_idname = "wm.blender_ai_apply_material"
    bl_label = "Generate Material"

    def execute(self, context):
        self.report({'INFO'}, "Material generation initiated")
        return {'FINISHED'}
