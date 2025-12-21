"""Gestione ingestione documentazione ufficiale Blender.

Questo modulo scarica e normalizza la documentazione dal sito ufficiale
`docs.blender.org` per manuale, API Python (`bpy`) e guida sviluppo add-on.
Produce artefatti JSON/SQLite con metadati di versione, categoria e tipo.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

DEFAULT_VERSIONS = ["3.6", "4.0", "4.1", "4.2", "4.3"]
MANUAL_BASE = "https://docs.blender.org/manual/en/{version}/"
API_BASE = "https://docs.blender.org/api/{version}/"
ADDON_GUIDE = "https://docs.blender.org/manual/en/{version}/advanced/scripting/addon_tutorial.html"


@dataclass
class DocEntry:
    version: str
    category: str
    type: str
    name: str
    docstring: str
    parameters: List[Dict[str, str]] = field(default_factory=list)
    methods: List[Dict[str, str]] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    path: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class BlenderDocsManager:
    """Scarica, normalizza e persiste la documentazione Blender."""

    def __init__(self, storage_dir: str | Path = "data/blender_docs"):
        self.storage_dir = Path(storage_dir)
        self.raw_dir = self.storage_dir / "raw"
        self.parsed_dir = self.storage_dir / "parsed"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for path in (self.storage_dir, self.raw_dir, self.parsed_dir):
            path.mkdir(parents=True, exist_ok=True)

    def _fetch(self, url: str, retries: int = 3, timeout: int = 20) -> str:
        last_exc: Exception | None = None
        for attempt in range(retries):
            try:
                resp = requests.get(url, timeout=timeout)
                resp.raise_for_status()
                return resp.text
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                time.sleep(1 + attempt)
        raise RuntimeError(f"Unable to fetch {url}: {last_exc}") from last_exc

    def _save_raw(self, version: str, slug: str, content: str) -> None:
        target = self.raw_dir / version
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{slug}.html").write_text(content, encoding="utf-8")

    def _parse_functions(self, soup: BeautifulSoup, version: str, category: str, path: str) -> List[DocEntry]:
        entries: List[DocEntry] = []
        for section in soup.select("dl.function, dl.method, dl.class"):
            signature = section.find("dt")
            description = section.find("dd")
            name = signature.get_text(" ", strip=True) if signature else "unknown"
            docstring = description.get_text("\n", strip=True) if description else ""
            params = []
            for param in section.select("em.parameter"):
                params.append({"name": param.get_text(strip=True), "type": "unknown", "description": ""})
            entries.append(
                DocEntry(
                    version=version,
                    category=category,
                    type=self._infer_type(section),
                    name=name,
                    docstring=docstring,
                    parameters=params,
                    metadata={"source": path},
                    path=path,
                )
            )
        return entries

    @staticmethod
    def _infer_type(section: BeautifulSoup) -> str:
        if "class" in section.get("class", []):
            return "class"
        if "method" in section.get("class", []):
            return "method"
        if "function" in section.get("class", []):
            return "function"
        return "section"

    def scrape_manual_sections(self, version: str, paths: Iterable[Tuple[str, str]]) -> List[DocEntry]:
        """Scarica e parse sezioni del manuale."""
        entries: List[DocEntry] = []
        for category, path in paths:
            url = MANUAL_BASE.format(version=version) + path
            html = self._fetch(url)
            self._save_raw(version, f"{category}-{path.replace('/', '_')}", html)
            soup = BeautifulSoup(html, "html.parser")
            entries.extend(self._parse_functions(soup, version, category, path))
        return entries

    def scrape_bpy_reference(self, version: str, root: str = "") -> List[DocEntry]:
        """Scarica riferimento bpy principale."""
        url = API_BASE.format(version=version) + root
        html = self._fetch(url)
        self._save_raw(version, f"bpy{('_' + root.replace('/', '_')) if root else ''}", html)
        soup = BeautifulSoup(html, "html.parser")
        return self._parse_functions(soup, version, "bpy", root or "index.html")

    def scrape_addon_guide(self, version: str) -> List[DocEntry]:
        url = ADDON_GUIDE.format(version=version)
        html = self._fetch(url)
        self._save_raw(version, "addon_guide", html)
        soup = BeautifulSoup(html, "html.parser")
        entries: List[DocEntry] = []
        for section in soup.select("section"):
            heading = section.find(["h1", "h2", "h3"])
            body = section.get_text("\n", strip=True)
            entries.append(
                DocEntry(
                    version=version,
                    category="addon-dev",
                    type="section",
                    name=heading.get_text(strip=True) if heading else "Add-on Development",
                    docstring=body,
                    examples=[],
                    metadata={"source": "addon_guide"},
                    path="addon_guide",
                )
            )
        return entries

    def save_entries(self, version: str, entries: List[DocEntry]) -> Path:
        target = self.parsed_dir / f"{version}.json"
        payload = [entry.to_dict() for entry in entries]
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._write_manifest(version, len(entries))
        return target

    def _write_manifest(self, version: str, count: int) -> None:
        manifest_path = self.storage_dir / "manifest.json"
        manifest = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest[version] = {"count": count, "updated_at": int(time.time())}
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def load_entries(self, version: str) -> List[DocEntry]:
        target = self.parsed_dir / f"{version}.json"
        if not target.exists():
            return []
        raw = json.loads(target.read_text(encoding="utf-8"))
        return [DocEntry(**entry) for entry in raw]

    def sync_sqlite(self, version: str, db_path: str | Path | None = None) -> Path:
        db_path = Path(db_path or (self.storage_dir / "blender_docs.sqlite"))
        entries = self.load_entries(version)
        conn = sqlite3.connect(db_path)
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS docs (
                    version TEXT,
                    category TEXT,
                    type TEXT,
                    name TEXT,
                    docstring TEXT,
                    parameters TEXT,
                    methods TEXT,
                    examples TEXT,
                    embedding TEXT,
                    metadata TEXT,
                    path TEXT
                )
                """
            )
            conn.execute("DELETE FROM docs WHERE version = ?", (version,))
            for entry in entries:
                conn.execute(
                    """
                    INSERT INTO docs (
                        version, category, type, name, docstring, parameters,
                        methods, examples, embedding, metadata, path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.version,
                        entry.category,
                        entry.type,
                        entry.name,
                        entry.docstring,
                        json.dumps(entry.parameters),
                        json.dumps(entry.methods),
                        json.dumps(entry.examples),
                        json.dumps(entry.embedding),
                        json.dumps(entry.metadata),
                        entry.path,
                    ),
                )
        conn.close()
        return db_path

    def ingest_all(self, versions: Iterable[str] = DEFAULT_VERSIONS) -> Dict[str, Path]:
        outputs: Dict[str, Path] = {}
        for version in versions:
            manual_entries = self.scrape_manual_sections(
                version,
                [
                    ("modifiers", "modeling/modifiers/introduction.html"),
                    ("geometry-nodes", "modeling/geometry_nodes/index.html"),
                    ("shaders", "render/shader_nodes/index.html"),
                    ("animation", "animation/index.html"),
                    ("import-export", "files/import_export/index.html"),
                ],
            )
            bpy_entries = self.scrape_bpy_reference(version, "index.html")
            addon_entries = self.scrape_addon_guide(version)
            all_entries = manual_entries + bpy_entries + addon_entries
            outputs[version] = self.save_entries(version, all_entries)
            self.sync_sqlite(version)
        return outputs

    def compatibility_matrix(self, versions: Iterable[str] = DEFAULT_VERSIONS) -> Dict[str, List[str]]:
        matrix: Dict[str, List[str]] = {}
        for version in versions:
            for entry in self.load_entries(version):
                matrix.setdefault(entry.name, []).append(version)
        return matrix

    def diff_versions(self, older: str, newer: str) -> Dict[str, List[str]]:
        """Rileva differenze fra due versioni (add/remove)."""
        old_names = {entry.name for entry in self.load_entries(older)}
        new_names = {entry.name for entry in self.load_entries(newer)}
        return {
            "added": sorted(new_names - old_names),
            "removed": sorted(old_names - new_names),
            "unchanged": sorted(old_names & new_names),
        }

    @staticmethod
    def stable_flag(version: str, added: str | None = None) -> Dict[str, str]:
        stable = "true" if version >= "4.0" else "false"
        return {"stable": stable, "added": added or version}

    def hash_entry(self, entry: DocEntry) -> str:
        blob = json.dumps(entry.to_dict(), sort_keys=True).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()


def default_manager() -> BlenderDocsManager:
    """Factory con path di progetto."""
    root = Path(os.getenv("BLENDERAI_DOCS_DIR", "data/blender_docs"))
    return BlenderDocsManager(storage_dir=root)
