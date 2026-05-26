from __future__ import annotations

import os
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PARENT = PROJECT_ROOT.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))


def _simple_prop(default=None, **kwargs):
    return kwargs.get("default", default)


class _FakeReportMixin:
    def __init__(self) -> None:
        self._reports: List[tuple] = []

    def report(self, level, message=None):
        self._reports.append((level, message))
        return None


class FakeOperator(_FakeReportMixin):
    bl_idname = ""
    bl_label = ""

    def __init__(self) -> None:
        super().__init__()


class FakePanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"

    def __init__(self) -> None:
        self.layout = FakeLayout()


class FakeLayout:
    def __init__(self) -> None:
        self.items = []

    def box(self):
        return self

    def column(self, align=False):
        return self

    def row(self, align=False):
        return self

    def prop(self, obj, attr, **kwargs):
        self.items.append(("prop", attr))
        return None

    def label(self, text="", icon=None):
        self.items.append(("label", text, icon))
        return None

    def operator(self, name, **kwargs):
        self.items.append(("operator", name, kwargs))
        op = FakeOperator()
        op.bl_idname = name
        return op


@dataclass
class FakeMaterial:
    name: str
    use_nodes: bool = False
    node_tree: types.SimpleNamespace = field(
        default_factory=lambda: types.SimpleNamespace(nodes=[], links=[])
    )


@dataclass
class FakeModifier:
    type: str


class FakeObject:
    def __init__(
        self,
        name: str,
        obj_type: str = "MESH",
        location=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
        modifiers: Sequence[str] | None = None,
        materials: Sequence[str] | None = None,
    ):
        self.name = name
        self.type = obj_type
        self.location = np.array(location, dtype=float)
        self.rotation_euler = np.array(rotation, dtype=float)
        self.scale = np.array(scale, dtype=float)
        self._modifiers = modifiers
        mat_objs = [types.SimpleNamespace(name=name) for name in (materials or [])]
        self.data = types.SimpleNamespace(
            materials=mat_objs, vertices=[1, 2, 3], edges=[1, 2], polygons=[1]
        )

    def keyframe_insert(self, data_path=None, frame=None):
        return True

    def select_set(self, state):
        pass

    @property
    def modifiers(self):
        class Mods(list):
            def new(self, name, type):
                self.append(name)
                return type

        return Mods([FakeModifier(m) for m in (self._modifiers or [])])


class FakeData:
    def __init__(self) -> None:
        self.materials: list[FakeMaterial] = [
            FakeMaterial(
                name="MatA",
                use_nodes=True,
                node_tree=types.SimpleNamespace(nodes=[1, 2]),
            )
        ]
        self.lights: list[str] = ["Key"]
        self.cameras: list[str] = ["Cam"]
        self.collections: list[str] = ["Collection"]
        self.armatures = types.SimpleNamespace(
            new=lambda name, **kwargs: types.SimpleNamespace(name=name)
        )


class FakeContext:
    def __init__(self, scene, active_object=None):
        self.scene = scene
        self.active_object = active_object
        import types

        self.collection = types.SimpleNamespace(
            objects=types.SimpleNamespace(link=lambda obj: None)
        )
        self.view_layer = types.SimpleNamespace(
            objects=types.SimpleNamespace(active=None)
        )


class FakeRender:
    def __init__(self, engine="CYCLES", resolution_x=1920, resolution_y=1080, fps=24):
        self.engine = engine
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.fps = fps


class FakeScene:
    def __init__(self) -> None:
        self.name = "TestScene"
        self.objects: list[FakeObject] = []
        self.world = types.SimpleNamespace(name="World", use_nodes=False)
        self.use_nodes = False
        self.node_tree = None
        self.render = FakeRender()
        self.cycles = types.SimpleNamespace(samples=64)
        self.frame_end = 1
        # Default addon properties commonly read/written by operators
        self.ai_openai_key = ""
        self.ai_anthropic_key = ""
        self.ai_google_key = ""
        self.ai_temperature = 0.2
        self.ai_model = "gpt-4"
        self.ai_ensemble_enabled = False
        self.ai_ensemble_weights = ""
        self.ai_semantic_cache_enabled = False
        self.ai_semantic_cache_threshold = 0.82
        self.ai_collab_enabled = False
        self.ai_collab_host = "localhost"
        self.ai_collab_port = 8765
        self.ai_collab_user = "tester"
        self.ai_collab_project = "demo"
        self.ai_role = "creator"
        self.ai_rate_limit = 120
        self.ai_prompt = "Test prompt"
        self.ai_last_response = ""
        self.ai_last_provider = ""
        self.ai_last_model = ""
        self.ai_last_cached = False
        self.ai_scene_snapshot = ""
        self.ai_doc_context = ""
        self.ai_doc_hints = ""
        self.ai_preview_code = ""
        self.ai_preview_description = ""
        self.ai_node_graph = ""
        self.ai_node_suggestions = ""
        self.ai_asset_query = ""
        self.ai_asset_results = ""
        self.ai_render_report = ""
        self.ai_batch_script = ""
        self.ai_perf_stats = ""
        self.ai_overlay_preview = ""
        self.ai_keyframe_preview = ""
        self.ai_node_heatmap = ""
        self.ai_usage_analytics = ""
        self.ai_export_path = ""
        self.ai_blender_version = "4.2"
        self.ai_doc_context = ""
        self.ai_doc_hints = ""
        self.ai_collab_enabled = False
        self.ai_collab_project = "default"


def _install_fake_bpy():
    if "bpy" in sys.modules:
        return sys.modules["bpy"]
    module = types.SimpleNamespace()
    module.types = types.SimpleNamespace(
        Operator=FakeOperator,
        Panel=FakePanel,
        Scene=FakeScene,
        Object=FakeObject,
        Context=FakeContext,
    )
    module.props = types.SimpleNamespace(
        StringProperty=lambda **kwargs: _simple_prop("", **kwargs),
        BoolProperty=lambda **kwargs: _simple_prop(False, **kwargs),
        EnumProperty=lambda **kwargs: _simple_prop(
            kwargs.get("items", [("", "", "")])[0][0] if kwargs.get("items") else None,
            **kwargs,
        ),
        IntProperty=lambda **kwargs: _simple_prop(0, **kwargs),
        FloatProperty=lambda **kwargs: _simple_prop(0.0, **kwargs),
    )
    module.data = FakeData()
    module.data.armatures = types.SimpleNamespace(
        new=lambda name, **kwargs: types.SimpleNamespace(name=name)
    )
    module.utils = types.SimpleNamespace(
        register_class=lambda cls: None, unregister_class=lambda cls: None
    )
    sys.modules["bpy"] = module
    return module


@pytest.fixture(scope="session", autouse=True)
def fake_bpy_module(tmp_path_factory):
    os.environ.setdefault("BLENDERAI_DOCS_DIR", str(tmp_path_factory.mktemp("docs")))
    return _install_fake_bpy()


@pytest.fixture()
def sample_scene(fake_bpy_module):
    scene = FakeScene()
    scene.objects = [
        FakeObject("Cube", "MESH", modifiers=["SUBSURF"], materials=["MatA"]),
        FakeObject("Light", "LIGHT"),
    ]
    return scene


@pytest.fixture()
def fake_context(sample_scene):
    return FakeContext(scene=sample_scene, active_object=sample_scene.objects[0])


@pytest.fixture()
def tmp_docs_dir(tmp_path, monkeypatch):
    root = tmp_path / "docs"
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("BLENDERAI_DOCS_DIR", str(root))
    return root
