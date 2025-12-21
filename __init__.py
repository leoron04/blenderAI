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
Version: 2.3.0
License: MIT
"""

bl_info = {
    "name": "BlenderAI - Intelligent Assistant",
    "blender": (3, 0, 0),
    "category": "Development",
    "version": (2, 3, 0),
    "author": "leoron04",
    "description": "AI-powered intelligent assistant for Blender with ChatGPT, Gemini, Claude integration",
    "wiki_url": "https://github.com/leoron04/blenderAI",
    "tracker_url": "https://github.com/leoron04/blenderAI/issues",
}

import os
import sys
import logging
import traceback

try:  # pragma: no cover - handled in tests via mock
    import bpy
except ImportError:  # pragma: no cover - fallback for non-Blender env
    import types

    class _MockOperator:
        bl_idname = ""
        bl_label = ""

        def report(self, *_args, **_kwargs):
            return None

    class _MockPanel:
        def __init__(self):
            self.layout = None

    bpy = types.SimpleNamespace(
        types=types.SimpleNamespace(
            Operator=_MockOperator,
            Panel=_MockPanel,
            Scene=object,
            Object=object,
            Context=object,
        ),
        props=types.SimpleNamespace(
            StringProperty=lambda **kwargs: kwargs.get("default", ""),
            BoolProperty=lambda **kwargs: kwargs.get("default", False),
            EnumProperty=lambda **kwargs: kwargs.get("default", None),
            IntProperty=lambda **kwargs: kwargs.get("default", 0),
            FloatProperty=lambda **kwargs: kwargs.get("default", 0.0),
        ),
        data=types.SimpleNamespace(materials=[], lights=[], cameras=[], collections=[]),
        utils=types.SimpleNamespace(register_class=lambda cls: None, unregister_class=lambda cls: None),
    )
    sys.modules["bpy"] = bpy
from . import config
from . import operators
from . import ui
from . import node_graph_visualizer
from . import animation_generator
from . import asset_manager
from . import render_optimizer
from . import performance_monitor
from . import visualization
from . import enterprise

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
    *visualization.classes,
    *enterprise.classes,
)


def register():
    _debug("Registering BlenderAI classes")
    _debug("sys.path head: %s", sys.path[:5])
    """Register all BlenderAI classes and scene properties.

    Called by Blender when the addon is enabled. Registers all operator classes,
    panel classes, and initializes scene properties for API configuration.
    """

    for cls in classes:
        bpy.utils.register_class(cls)

    model_items = config.api_config.get_available_models()
    bpy.types.Scene.ai_model = bpy.props.EnumProperty(
        items=model_items if model_items else [("auto", "Auto Select", "")],
        default="auto" if ("auto", "Auto Select", "") in model_items else "gpt-4",
    )
    bpy.types.Scene.ai_blender_version = bpy.props.StringProperty(
        name="Blender Version",
        description="Versione target Blender per il recupero documentazione",
        default="4.2",
    )

    bpy.types.Scene.ai_openai_key = bpy.props.StringProperty(name="OpenAI API Key", default="", subtype="PASSWORD")
    bpy.types.Scene.ai_anthropic_key = bpy.props.StringProperty(name="Anthropic API Key", default="", subtype="PASSWORD")
    bpy.types.Scene.ai_google_key = bpy.props.StringProperty(name="Google API Key", default="", subtype="PASSWORD")
    bpy.types.Scene.ai_temperature = bpy.props.FloatProperty(
        name="Temperature", description="Creatività modello", default=0.4, min=0.0, max=1.0
    )
    bpy.types.Scene.ai_ensemble_enabled = bpy.props.BoolProperty(
        name="Ensemble Multi-modello",
        description="Combina più provider con voting pesato",
        default=False,
    )
    bpy.types.Scene.ai_ensemble_weights = bpy.props.StringProperty(
        name="Pesi Ensemble (JSON)",
        description='Esempio: {"anthropic":1.5,"openai":1,"gemini":0.8}',
        default="",
    )
    bpy.types.Scene.ai_semantic_cache_enabled = bpy.props.BoolProperty(
        name="Semantic Cache",
        description="Riusa risposte simili con embedding leggeri",
        default=False,
    )
    bpy.types.Scene.ai_semantic_cache_threshold = bpy.props.FloatProperty(
        name="Soglia Similarità",
        description="Threshold cosine per cache semantica (0-1)",
        default=0.82,
        min=0.5,
        max=0.99,
    )
    bpy.types.Scene.ai_collab_enabled = bpy.props.BoolProperty(
        name="Realtime Collaboration",
        description="Abilita WebSocket broadcast suggerimenti",
        default=False,
    )
    bpy.types.Scene.ai_collab_host = bpy.props.StringProperty(
        name="Collab Host",
        default="127.0.0.1",
    )
    bpy.types.Scene.ai_collab_port = bpy.props.IntProperty(
        name="Collab Port",
        default=8765,
        min=1024,
        max=65535,
    )
    bpy.types.Scene.ai_collab_user = bpy.props.StringProperty(
        name="Collab User",
        default="guest",
    )
    bpy.types.Scene.ai_collab_project = bpy.props.StringProperty(
        name="Project ID",
        default="default",
    )
    bpy.types.Scene.ai_role = bpy.props.EnumProperty(
        name="Ruolo",
        items=[("admin", "Admin", ""), ("creator", "Creator", ""), ("viewer", "Viewer", "")],
        default="creator",
    )
    bpy.types.Scene.ai_rate_limit = bpy.props.IntProperty(
        name="Rate Limit (hour)",
        default=120,
        min=1,
        max=10000,
    )
    bpy.types.Scene.ai_prompt = bpy.props.StringProperty(name="Prompt", default="Analizza la scena e proponi azioni.")
    bpy.types.Scene.ai_last_response = bpy.props.StringProperty(name="Last Response", default="")
    bpy.types.Scene.ai_last_provider = bpy.props.StringProperty(name="Last Provider", default="")
    bpy.types.Scene.ai_last_model = bpy.props.StringProperty(name="Last Model", default="")
    bpy.types.Scene.ai_last_cached = bpy.props.BoolProperty(name="Cached", default=False)
    bpy.types.Scene.ai_scene_snapshot = bpy.props.StringProperty(name="Scene Snapshot", default="")
    bpy.types.Scene.ai_doc_context = bpy.props.StringProperty(
        name="Doc Context",
        description="Contesto documentazione Blender recuperato via RAG",
        default="",
    )
    bpy.types.Scene.ai_doc_hints = bpy.props.StringProperty(
        name="Doc Hints",
        description="Suggerimenti documentazione basati sulla scena",
        default="",
    )
    bpy.types.Scene.ai_preview_code = bpy.props.StringProperty(name="Preview Code", default="")
    bpy.types.Scene.ai_preview_description = bpy.props.StringProperty(name="Preview Description", default="")
    bpy.types.Scene.ai_node_graph = bpy.props.StringProperty(name="Node Graph", default="")
    bpy.types.Scene.ai_node_suggestions = bpy.props.StringProperty(name="Node Suggestions", default="")
    bpy.types.Scene.ai_asset_query = bpy.props.StringProperty(name="Asset Query", default="")
    bpy.types.Scene.ai_asset_results = bpy.props.StringProperty(name="Asset Results", default="")
    bpy.types.Scene.ai_render_report = bpy.props.StringProperty(name="Render Report", default="")
    bpy.types.Scene.ai_batch_script = bpy.props.StringProperty(name="Batch Script", default="")
    bpy.types.Scene.ai_perf_stats = bpy.props.StringProperty(name="Performance Stats", default="")
    bpy.types.Scene.ai_overlay_preview = bpy.props.StringProperty(name="Overlay Preview", default="")
    bpy.types.Scene.ai_keyframe_preview = bpy.props.StringProperty(name="Keyframe Preview", default="")
    bpy.types.Scene.ai_node_heatmap = bpy.props.StringProperty(name="Node Heatmap", default="")
    bpy.types.Scene.ai_usage_analytics = bpy.props.StringProperty(name="Usage Analytics", default="")
    bpy.types.Scene.ai_export_path = bpy.props.StringProperty(name="Export Path", default="")


def unregister():
    _debug("Unregistering BlenderAI classes")
    """Unregister all BlenderAI classes and clean up scene properties.

    Called by Blender when the addon is disabled. Unregisters all classes
    in reverse order and removes all scene properties created during registration.
    """

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    attrs = [
        "ai_model",
        "ai_blender_version",
        "ai_openai_key",
        "ai_anthropic_key",
        "ai_google_key",
        "ai_blender_version",
        "ai_temperature",
        "ai_ensemble_enabled",
        "ai_ensemble_weights",
        "ai_semantic_cache_enabled",
        "ai_semantic_cache_threshold",
        "ai_collab_enabled",
        "ai_collab_host",
        "ai_collab_port",
        "ai_collab_user",
        "ai_collab_project",
        "ai_role",
        "ai_rate_limit",
        "ai_prompt",
        "ai_last_response",
        "ai_last_provider",
        "ai_last_model",
        "ai_last_cached",
        "ai_scene_snapshot",
        "ai_doc_context",
        "ai_doc_hints",
        "ai_preview_code",
        "ai_preview_description",
        "ai_node_graph",
        "ai_node_suggestions",
        "ai_asset_query",
        "ai_asset_results",
        "ai_render_report",
        "ai_batch_script",
        "ai_perf_stats",
        "ai_overlay_preview",
        "ai_keyframe_preview",
        "ai_node_heatmap",
        "ai_usage_analytics",
        "ai_export_path",
    ]
    for attr in attrs:
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)
