bl_info = {
    "name": "BlenderAI - Intelligent Assistant",
    "blender": (3, 0, 0),
    "category": "Development",
    "version": (1, 0, 0),
    "author": "leoron04",
    "description": "AI-powered intelligent assistant for Blender with ChatGPT, Gemini integration",
    "wiki_url": "https://github.com/leoron04/blenderAI",
    "tracker_url": "https://github.com/leoron04/blenderAI/issues",
}

import bpy
from . import operators
from . import ui
from . import utils

classes = [
    operators.BLENDER_AI_OT_chat,
    operators.BLENDER_AI_OT_apply_suggestion,
    ui.BLENDER_AI_PT_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ai_history = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.ai_api_key = bpy.props.StringProperty(default="")
    bpy.types.Scene.ai_model = bpy.props.EnumProperty(
        items=[("chatgpt", "ChatGPT", ""), ("gemini", "Google Gemini", "")],
        default="chatgpt"
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.ai_history
    del bpy.types.Scene.ai_api_key
    del bpy.types.Scene.ai_model

if __name__ == "__main__":
    register()
