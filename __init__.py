bl_info = {
    "name": "BlenderAI - Intelligent Assistant",
    "blender": (3, 0, 0),
    "category": "Development",
    "version": (1, 0, 0),
    "author": "leoron04",
    "description": "AI-powered intelligent assistant for Blender with ChatGPT, Gemini, Claude integration",
    "wiki_url": "https://github.com/leoron04/blenderAI",
    "tracker_url": "https://github.com/leoron04/blenderAI/issues",
}

import bpy
from . import operators
from . import ui
from . import utils
from . import config


classes = [
    operators.BLENDER_AI_OT_chat,
    operators.BLENDER_AI_OT_apply_suggestion,
    ui.BLENDER_AI_PT_panel,
]


def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Initialize configuration
    config.api_config.is_configured()
    
    # Add scene properties
    bpy.types.Scene.ai_history = bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup
    )
    
    # API configuration
    bpy.types.Scene.ai_api_key = bpy.props.StringProperty(
        default="",
        description="API key for AI model"
    )
    
    # Model selection with enum
    model_items = config.api_config.get_available_models()
    bpy.types.Scene.ai_model = bpy.props.EnumProperty(
        items=model_items if model_items else [("auto", "Auto Select", "")],
        default="auto" if ("auto", "Auto Select") in model_items else "gpt-4"
    )
    
    # Temperature setting
    bpy.types.Scene.ai_temperature = bpy.props.FloatProperty(
        name="Temperature",
        description="Model temperature for creativity (0.0 = deterministic, 1.0 = creative)",
        default=0.7,
        min=0.0,
        max=1.0
    )
    
    # Auto mode toggle
    bpy.types.Scene.ai_auto_mode = bpy.props.BoolProperty(
        name="Auto Mode",
        description="Automatically select best model for task",
        default=True
    )


def unregister():
    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Clean up properties
    if hasattr(bpy.types.Scene, "ai_history"):
        del bpy.types.Scene.ai_history
    if hasattr(bpy.types.Scene, "ai_api_key"):
        del bpy.types.Scene.ai_api_key
    if hasattr(bpy.types.Scene, "ai_model"):
        del bpy.types.Scene.ai_model
    if hasattr(bpy.types.Scene, "ai_temperature"):
        del bpy.types.Scene.ai_temperature
    if hasattr(bpy.types.Scene, "ai_auto_mode"):
        del bpy.types.Scene.ai_auto_mode
