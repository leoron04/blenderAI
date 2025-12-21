"""UI Panel for BlenderAI - Beautiful, Simple, Powerful Interface.

Provides an intuitive interface for AI configuration, model selection,
and interactive chat with the AI assistant.
"""

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, EnumProperty, BoolProperty

from . import config


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
        row.label(text="🎯 BlenderAI Control Center")
        
        # Configuration Section
        box = layout.box()
        box.label(text="⚙️ Configuration", icon='PREFERENCES')
        
        # API Key Input
        col = box.column(align=True)
        col.label(text="API Configuration:")
        col.prop(scene, "ai_api_key", text="API Key", toggle=True)
        
        # Model Selection with Recommendations
        col = box.column(align=True)
        col.label(text="Model Selection:")
        
        # Get available models
        available_models = config.api_config.get_available_models()
        model_enum = [(m[0], m[1], "") for m in available_models]
        
        if available_models:
            col.prop(scene, "ai_model", text="Choose Model")
            
            # Show model info if available
            current_model = scene.ai_model
            model_info = config.get_model_info(current_model)
            
            if model_info:
                info_box = box.box()
                info_box.label(text=f"{model_info.icon} {model_info.name} Info")
                info_box.label(text=f"Provider: {model_info.provider}")
                info_box.label(text=f"Speed: {model_info.speed}")
                info_box.label(text=f"Quality: {model_info.quality}")
                info_box.label(text=f"Cost: {model_info.cost}")
                
                if model_info.recommended_for:
                    info_box.label(text="Recommended for:")
                    for rec in model_info.recommended_for:
                        info_box.label(text=f"  • {rec}", icon='CHECKMARK')
        else:
            col.label(text="⚠️ No API configured", icon='ERROR')
        
        # Temperature Control
        col = box.column(align=True)
        col.label(text="Creativity Control:")
        col.prop(scene, "ai_temperature", text="Temperature", slider=True)
        col.label(text="0.0 = Deterministic | 1.0 = Creative", icon='INFO')
        
        # Auto Mode Section
        box = layout.box()
        box.label(text="🚀 Auto Mode", icon='PLAY')
        col = box.column(align=True)
        col.prop(scene, "ai_auto_mode", text="Enable Auto Selection")
        
        if scene.ai_auto_mode:
            info_box = box.box()
            recommended = config.get_recommended_model()
            info_box.label(text=f"✨ Recommended: {recommended}")
            info_box.label(text="Auto mode selects the best model for your task", icon='INFO')
        
        # Chat Section
        box = layout.box()
        box.label(text="💬 Chat Interface", icon='WORDWRAP_ON')
        col = box.column(align=True)
        col.label(text="Chat with AI Assistant:")
        col.scale_y = 1.5
        col.operator("blender_ai.ot_chat", text="💭 Chat", icon='PLAY')
        
        # Quick Actions
        box = layout.box()
        box.label(text="⚡ Quick Actions", icon='LIGHTNING')
        row = box.row(align=True)
        row.operator("blender_ai.ot_apply_suggestion", text="Apply", icon='CHECKMARK')
        row.operator("blender_ai.ot_apply_suggestion", text="Clear", icon='X')
        
        # Status Section
        if config.api_config.is_configured():
            box = layout.box()
            box.label(text="✅ Status: Configured", icon='CHECKMARK')
        else:
            box = layout.box()
            box.label(text="⚠️ Status: Needs Setup", icon='ERROR')
            box.label(text="Please configure at least one API key", icon='INFO')


class BLENDER_AI_PT_help_panel(Panel):
    """Help and Information Panel"""
    
    bl_label = "ℹ️ Help & Documentation"
    bl_idname = "BLENDER_AI_PT_help_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BlenderAI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Getting Started", icon='HELP')
        col = box.column(align=True)
        col.label(text="1. Configure an API key")
        col.label(text="2. Select a model")
        col.label(text="3. Start chatting!")
        
        box = layout.box()
        box.label(text="Keyboard Shortcuts", icon='SHORTCUT')
        col = box.column(align=True)
        col.label(text="Ctrl+Alt+A: Open AI Chat")
        col.label(text="Ctrl+Alt+S: Apply Suggestion")
        
        box = layout.box()
        box.label(text="Documentation", icon='TEXT')
        col = box.column(align=True)
        col.label(text="Visit: github.com/leoron04/blenderAI")
