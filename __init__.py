"""BlenderAI - Intelligent AI Assistant for Blender

Main entry point for the BlenderAI addon. Handles registration of all classes,
scene properties, and module initialization for the Blender addon system.

Features:
    - Multi-AI provider support (Claude, GPT-4, Gemini) with intelligent fallback
    - Scene analysis and intelligent suggestions
    - Animation generation, asset management, and render optimization
    - Advanced node graph visualization and performance monitoring

Requirements:
    - Blender 3.6+
    - Python 3.10+
    - API keys for at least one supported AI provider

Author: leoron04
Version: 1.0.0
License: MIT
"""

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

import os
import sys
import logging
import traceback
import bpy
from . import config
from . import operators
from . import ui
from . import node_graph_visualizer
from . import animation_generator
from . import asset_manager
from . import render_optimizer
from . import performance_monitor

_logger = logging.getLogger("blenderAI.import")
if not _logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[blenderAI] %(message)s"))
    _logger.addHandler(handler)
_logger.setLevel(logging.INFO)

def _debug(msg: str, *args) -> None:
    if os.getenv("BLENDERAI_DEBUG", "0") == "1" or os.getenv("BLENDERAI_DEBUG_IMPORT", "0") == "1":
        _logger.info(msg, *args)

_debug("Add-on import start")
_debug("Add-on __file__: %s", __file__)
_debug("Current sys.path head: %s", sys.path[:5])
_debug("Working dir: %s", os.getcwd())

try:
    from . import config
    from . import operators
    from . import ui
    from . import node_graph_visualizer
    from . import animation_generator
    from . import asset_manager
    from . import render_optimizer
    from . import performance_monitor
except Exception:  # noqa: BLE001
    _logger.error("Errore durante l'import dei moduli BlenderAI:\n%s", traceback.format_exc())
    raise

classes = (
    *operators.classes,
    *ui.classes,
    *node_graph_visualizer.classes,
    *animation_generator.classes,
    *asset_manager.classes,
    *render_optimizer.classes,
    *performance_monitor.classes,
)


def register():
    _debug("Registering BlenderAI classes")
    _debug("sys.path head: %s", sys.path[:5])
        """Register all BlenderAI classes and scene properties.
    
    Called by Blender when the addon is enabled. Registers all operator classes,
    panel classes, and initializes scene properties for API configuration.
    
    Returns:
        None
    """
    
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
    bpy.types.Scene.ai_node_graph = bpy.props.StringProperty(name="Node Graph", default="")
    bpy.types.Scene.ai_node_suggestions = bpy.props.StringProperty(name="Node Suggestions", default="")
    bpy.types.Scene.ai_asset_query = bpy.props.StringProperty(name="Asset Query", default="")
    bpy.types.Scene.ai_asset_results = bpy.props.StringProperty(name="Asset Results", default="")
    bpy.types.Scene.ai_render_report = bpy.props.StringProperty(name="Render Report", default="")
    bpy.types.Scene.ai_batch_script = bpy.props.StringProperty(name="Batch Script", default="")
    bpy.types.Scene.ai_perf_stats = bpy.props.StringProperty(name="Performance Stats", default="")


def unregister():
    _debug("Unregistering BlenderAI classes")
        """Unregister all BlenderAI classes and clean up scene properties.
    
    Called by Blender when the addon is disabled. Unregisters all classes
    in reverse order and removes all scene properties created during registration.
    
    Returns:
        None
    """
    
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
        "ai_node_graph",
        "ai_node_suggestions",
        "ai_asset_query",
        "ai_asset_results",
        "ai_render_report",
        "ai_batch_script",
        "ai_perf_stats",
    ]
    for attr in attrs:
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)
