#!/usr/bin/env bash
# Launch the RoboUsr FastAPI app (which runs the Telethon userbot).
# This script expects a Python venv in ./venv and an optional ./.env file.
# To install dependencies into the venv from pyproject.toml, run:
#   source venv/bin/activate
#   pip install .
set -euo pipefail

# Switch to project root (the directory of this script)
cd "$(dirname "$0")"

# Export variables from .env if present
if [[ -f .env ]]; then
  # Export all variables defined in .env to the environment
  set -a
  # shellcheck source=/dev/null
  . ./.env
  set +a
fi

# Ensure venv exists
if [[ ! -x "venv/bin/uvicorn" ]]; then
  echo "ERROR: venv not found or uvicorn not installed." >&2
  echo "Create venv and install project with:" >&2
  echo "  python -m venv venv" >&2
  echo "  source venv/bin/activate" >&2
  echo "  pip install ." >&2
  exit 1
fi

# Ensure Python can import from ./src
export PYTHONPATH="${PYTHONPATH:-}:$PWD/src"

# Pick host/port from env or defaults
APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"

exec ./venv/bin/uvicorn core.main:app --host "$APP_HOST" --port "$APP_PORT"
