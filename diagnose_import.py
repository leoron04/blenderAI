"""Diagnostica avanzata per capire perché Blender non trova il modulo BlenderAI.

Esegui con:
    python diagnose_import.py
oppure dentro Blender (Text Editor > Run Script).

Mostra:
- Nome cartella corrente e confronto con 'blenderAI'
- sys.path completo e prima occorrenza di blenderAI
- Risultato di importlib.util.find_spec('blenderAI')
- Dove fallisce l'import reale (traceback catturato)
- Percorsi addon Blender (se bpy disponibile)
- Salva log in ~/.config/blenderai_debug.log
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import traceback
from pathlib import Path

LOG_PATH = Path(os.path.expanduser("~/.config/blenderai_debug.log"))


def check_folder_name() -> str:
    here = Path(__file__).resolve().parent
    expected = "blenderAI"
    status = "OK" if here.name == expected else "WARN"
    return f"{status}: cartella addon = '{here.name}' (path: {here})"


def find_first_blenderai_in_path() -> str:
    for entry in sys.path:
        candidate = Path(entry) / "blenderAI"
        if candidate.exists():
            return f"Trovata directory blenderAI in sys.path: {candidate}"
    return "Nessuna directory blenderAI trovata in sys.path"


def spec_info() -> str:
    spec = importlib.util.find_spec("blenderAI")
    return f"importlib.find_spec('blenderAI') -> {spec}"


def import_trace() -> str:
    try:
        importlib.import_module("blenderAI")
        return "Import OK: blenderAI"
    except Exception:
        tb = traceback.format_exc()
        return f"Import FAILED: blenderAI\n{tb}"


def bpy_resources() -> str:
    try:
        import bpy  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return f"INFO: bpy non disponibile ({exc}). Esegui dentro Blender per percorsi addon esatti."
    user_addons = bpy.utils.user_resource("SCRIPTS", "addons")
    system_addons = bpy.utils.system_resource("SCRIPTS", "addons")
    return f"Blender addons user: {user_addons}\nBlender addons system: {system_addons}"


def main() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write("=== BlenderAI Import Diagnosis ===\n")
        log.write(f"{check_folder_name()}\n")
        log.write(f"{spec_info()}\n")
        log.write(f"{find_first_blenderai_in_path()}\n")
        log.write(f"{import_trace()}\n")
        log.write("sys.path completo:\n")
        for entry in sys.path:
            log.write(f" - {entry}\n")
        log.write(f"{bpy_resources()}\n")

    print("=== BlenderAI Import Diagnosis ===")
    print(check_folder_name())
    print(spec_info())
    print(find_first_blenderai_in_path())
    print(import_trace())
    print("sys.path completo:")
    for entry in sys.path:
        print(f" - {entry}")
    print()
    print(bpy_resources())
    print(f"Log scritto in: {LOG_PATH}")


if __name__ == "__main__":
    main()
