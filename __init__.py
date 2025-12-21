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
from . import config
from . import operators
from . import ui


classes = (
    *operators.classes,
    *ui.classes,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    model_items = config.api_config.get_available_models()
    bpy.types.Scene.ai_model = bpy.props.EnumProperty(
        items=model_items if model_items else [("auto", "Auto Select", "")],
        default="auto" if ("auto", "Auto Select", "") in model_items else "gpt-4",
    )

    bpy.types.Scene.ai_openai_key = bpy.props.StringProperty(name="OpenAI API Key", default="", subtype="PASSWORD")
    bpy.types.Scene.ai_anthropic_key = bpy.props.StringProperty(name="Anthropic API Key", default="", subtype="PASSWORD")
    bpy.types.Scene.ai_google_key = bpy.props.StringProperty(name="Google API Key", default="", subtype="PASSWORD")
    bpy.types.Scene.ai_temperature = bpy.props.FloatProperty(
        name="Temperature", description="Creatività modello", default=0.4, min=0.0, max=1.0
    )
    bpy.types.Scene.ai_prompt = bpy.props.StringProperty(name="Prompt", default="Analizza la scena e proponi azioni.")
    bpy.types.Scene.ai_last_response = bpy.props.StringProperty(name="Last Response", default="")
    bpy.types.Scene.ai_last_provider = bpy.props.StringProperty(name="Last Provider", default="")
    bpy.types.Scene.ai_last_model = bpy.props.StringProperty(name="Last Model", default="")
    bpy.types.Scene.ai_last_cached = bpy.props.BoolProperty(name="Cached", default=False)
    bpy.types.Scene.ai_scene_snapshot = bpy.props.StringProperty(name="Scene Snapshot", default="")
    bpy.types.Scene.ai_preview_code = bpy.props.StringProperty(name="Preview Code", default="")
    bpy.types.Scene.ai_preview_description = bpy.props.StringProperty(name="Preview Description", default="")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    attrs = [
        "ai_model",
        "ai_openai_key",
        "ai_anthropic_key",
        "ai_google_key",
        "ai_temperature",
        "ai_prompt",
        "ai_last_response",
        "ai_last_provider",
        "ai_last_model",
        "ai_last_cached",
        "ai_scene_snapshot",
        "ai_preview_code",
        "ai_preview_description",
    ]
    for attr in attrs:
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)
