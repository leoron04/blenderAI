"""Eseguibile semplice per la suite di test BlenderAI dentro/fuori da Blender.

Consente di usare il Python di sistema o quello bundle di Blender, applicando
le opzioni di coverage richieste e mantenendo la compatibilità con l'ambiente
senza `bpy`.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List


def build_command(python_bin: str, with_cov: bool, extra_args: List[str]) -> List[str]:
    cmd: List[str] = [python_bin, "-m", "pytest"]
    if with_cov:
        cmd += ["--cov=.", "--cov-report=term-missing"]
    cmd += extra_args
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="Runner unificato per i test BlenderAI")
    parser.add_argument(
        "--python",
        dest="python_bin",
        default=sys.executable,
        help="Interpreter Python da usare (es. quello di Blender)",
    )
    parser.add_argument("--no-cov", action="store_true", help="Disabilita i report di coverage")
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Argomenti addizionali passati direttamente a pytest",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.resolve()
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(project_root))
    env.setdefault("BLENDERAI_DOCS_DIR", str(project_root / "data" / "blender_docs"))

    cmd = build_command(args.python_bin, with_cov=not args.no_cov, extra_args=args.pytest_args)
    print(f"Esecuzione: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=project_root, env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
