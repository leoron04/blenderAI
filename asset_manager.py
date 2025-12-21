"""Smart Asset Manager MVP v0.1."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import bpy

ASSET_INDEX_PATH = os.path.expanduser("~/.config/blender_ai/assets_index.json")


def _ensure_index_path(path: str = ASSET_INDEX_PATH) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"assets": []}, f, indent=2)
    return path


@dataclass
class AssetLibraryIndex:
    """Gestione indice asset locale (JSON)."""

    path: str = ASSET_INDEX_PATH
    assets: List[Dict[str, str]] = field(default_factory=list)

    def load(self) -> None:
        index_path = _ensure_index_path(self.path)
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assets = data.get("assets", [])
        except (OSError, json.JSONDecodeError):
            self.assets = []

    def save(self) -> None:
        index_path = _ensure_index_path(self.path)
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump({"assets": self.assets}, f, indent=2)


class SemanticSearch:
    """Ricerca semantica semplificata via keyword matching."""

    @staticmethod
    def search(assets: List[Dict[str, str]], query: str) -> List[Dict[str, str]]:
        if not query:
            return assets[:5]
        query_tokens = query.lower().split()
        results: List[Dict[str, str]] = []
        for asset in assets:
            text = f"{asset.get('name','')} {asset.get('description','')} {asset.get('tags','')}".lower()
            if all(token in text for token in query_tokens):
                results.append(asset)
        return results[:10]


class BLENDER_AI_OT_search_assets(bpy.types.Operator):
    """Esegue ricerca nel catalogo asset locale."""

    bl_idname = "blender_ai.search_assets"
    bl_label = "Search Assets"

    def execute(self, context):
        scene = context.scene
        index = AssetLibraryIndex()
        index.load()
        results = SemanticSearch.search(index.assets, scene.ai_asset_query)
        scene.ai_asset_results = json.dumps(results, indent=2)[:4000]
        self.report({"INFO"}, f"Trovati {len(results)} asset.")
        return {"FINISHED"}


class BLENDER_AI_OT_import_asset(bpy.types.Operator):
    """Stub import asset: per MVP mostra nome selezionato."""

    bl_idname = "blender_ai.import_asset"
    bl_label = "Load Asset"

    asset_name: bpy.props.StringProperty(default="")

    def execute(self, context):
        self.report({"INFO"}, f"Import asset stub: {self.asset_name}")
        return {"FINISHED"}


class BLENDER_AI_PT_asset_library(bpy.types.Panel):
    bl_label = "📚 Asset Library"
    bl_idname = "BLENDER_AI_PT_asset_library"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderAI"
    bl_parent_id = "BLENDER_AI_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.prop(scene, "ai_asset_query", text="Search")
        box.operator(BLENDER_AI_OT_search_assets.bl_idname, icon="VIEWZOOM")
        box.prop(scene, "ai_asset_results", text="Results")
        box.operator(BLENDER_AI_OT_import_asset.bl_idname, icon="APPEND_BLEND")


classes = (
    BLENDER_AI_OT_search_assets,
    BLENDER_AI_OT_import_asset,
    BLENDER_AI_PT_asset_library,
)
