#!/usr/bin/env bash
# Start a local llama-cpp server that exposes an OpenAI-compatible API.
# Adjust LLAMA_MODEL_PATH/LLAMA_MODEL_NAME in .env or pass them in the environment.
# To install dependencies into the venv from pyproject.toml, run:
#   source venv/bin/activate
#   pip install .
set -euo pipefail

cd "$(dirname "$0")"

# Export variables from .env if present
if [[ -f .env ]]; then
  set -a
  # shellcheck source=/dev/null
  . ./.env
  set +a
fi

# Ensure venv exists
if [[ ! -x "venv/bin/python" ]]; then
  echo "ERROR: venv not found." >&2
  echo "Create venv and install project with:" >&2
  echo "  python -m venv venv" >&2
  echo "  source venv/bin/activate" >&2
  echo "  pip install ." >&2
  exit 1
fi

MODEL_PATH="${LLAMA_MODEL_PATH:-$PWD/models/model-q4_K.gguf}"
THREADS="${LLAMA_THREADS:-4}"
HOST="${LLAMA_HOST:-127.0.0.1}"
PORT="${LLAMA_PORT:-8001}"
ALIAS="${LLAMA_MODEL_NAME:-saiga-llama3-8b}"

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "ERROR: Model file not found at '$MODEL_PATH'." >&2
  echo "Download a GGUF model (e.g., Saiga LLaMA-3 8B) and set LLAMA_MODEL_PATH." >&2
  exit 1
fi

exec ./venv/bin/python -m llama_cpp.server \
  --model "$MODEL_PATH" \
  --model_alias "$ALIAS" \
  --chat_format=llama-3 \
  --host "$HOST" \
  --port "$PORT" \
  --n_threads "$THREADS"
