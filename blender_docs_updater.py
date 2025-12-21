"""Runner programmabile per aggiornare la documentazione Blender."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

import utils
from blender_docs_manager import DEFAULT_VERSIONS, BlenderDocsManager
from docs_embeddings import DocsEmbeddingIndex


def run_update(versions: Iterable[str], storage_dir: str | Path = "data/blender_docs") -> None:
    manager = BlenderDocsManager(storage_dir)
    utils.log_message(f"Avvio ingestione documentazione per versioni: {versions}", level="INFO")
    manager.ingest_all(versions)
    utils.log_message("Costruzione embedding...", level="INFO")
    index = DocsEmbeddingIndex(storage_dir)
    index.build(versions)
    utils.log_message("Aggiornamento completato.", level="INFO")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggiorna documentazione Blender e embedding.")
    parser.add_argument(
        "--versions",
        nargs="+",
        default=DEFAULT_VERSIONS,
        help="Versioni Blender da aggiornare (es: 4.0 4.1 4.2).",
    )
    parser.add_argument("--storage", default="data/blender_docs", help="Cartella di output artefatti.")
    args = parser.parse_args(argv)
    run_update(args.versions, storage_dir=args.storage)
    return 0


if __name__ == "__main__":
    sys.exit(main())
