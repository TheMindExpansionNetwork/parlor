#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_CANDIDATE="$REPO_ROOT/models/Gemma-4-E2B-it-abliterated.litertlm"

if [[ -z "${MODEL_PATH:-}" && -f "$MODEL_CANDIDATE" ]]; then
  export MODEL_PATH="$MODEL_CANDIDATE"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed or not on PATH."
  echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "Then run: source \"\$HOME/.local/bin/env\""
  exit 1
fi

cd "$REPO_ROOT/src"

echo "Repo root: $REPO_ROOT"
if [[ -n "${MODEL_PATH:-}" ]]; then
  echo "MODEL_PATH=$MODEL_PATH"
else
  echo "MODEL_PATH is not set. The server will look in the repo models folder first."
fi

echo "[1/2] Syncing dependencies with uv..."
uv sync

echo "[2/2] Starting server..."
exec uv run server.py
