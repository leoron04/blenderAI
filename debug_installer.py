"""Validatore di installazione BlenderAI.

Uso:
    python debug_installer.py

Controlla che la cartella addon si chiami esattamente `blenderAI`
e mostra i percorsi add-on di Blender (se bpy è disponibile).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def check_folder_name() -> str:
    current = Path(__file__).resolve().parent
    name = current.name
    expected = "blenderAI"
    if name != expected:
        return f"WARN: nome cartella '{name}' non corretto. Rinomina in '{expected}'. Path: {current}"
    return f"OK: cartella addon corretta: {current}"


def blender_paths() -> str:
    try:
        import bpy  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return f"INFO: bpy non disponibile ({exc}). Esegui dentro Blender o con Blender Python per percorsi precisi."

    user_addons = bpy.utils.user_resource("SCRIPTS", "addons")
    system_addons = bpy.utils.system_resource("SCRIPTS", "addons")
    active_addons = list(bpy.context.preferences.addons.keys())
    return (
        f"Blender user addons: {user_addons}\n"
        f"Blender system addons: {system_addons}\n"
        f"Addons attivi: {active_addons}\n"
    )


def main() -> None:
    print("=== BlenderAI Installer Debug ===")
    print(check_folder_name())
    print()
    print(blender_paths())


if __name__ == "__main__":
    main()
