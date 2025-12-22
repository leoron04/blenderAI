#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Avvio BlenderAI API server"

cd /app

if [[ -z "${OPENAI_API_KEY:-}" && -z "${ANTHROPIC_API_KEY:-}" && -z "${GOOGLE_API_KEY:-}" ]]; then
  echo "[entrypoint] Nessuna API key configurata (OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY)"
  echo "[entrypoint] Definire almeno una chiave per consentire le chiamate AI."
else
  echo "[entrypoint] API key rilevate: "
  [[ -n "${OPENAI_API_KEY:-}" ]] && echo " - OPENAI_API_KEY"
  [[ -n "${ANTHROPIC_API_KEY:-}" ]] && echo " - ANTHROPIC_API_KEY"
  [[ -n "${GOOGLE_API_KEY:-}" ]] && echo " - GOOGLE_API_KEY"
fi

if [[ "${RUN_MIGRATIONS:-0}" == "1" ]]; then
  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "[entrypoint] RUN_MIGRATIONS=1 ma DATABASE_URL non è definita, skip."
  else
    echo "[entrypoint] Eseguo migrazioni (placeholder)..."
    python - <<'PY'
import os
print("Nessuna migration definita per BlenderAI. DATABASE_URL=", os.environ.get("DATABASE_URL", ""))
PY
  fi
fi

exec python -m blenderAI.api_server
