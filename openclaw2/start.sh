#!/bin/bash
# OpenClaw 2 standalone start
# If running as part of AI Employee, use the root-level ./start.sh instead.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV="$SCRIPT_DIR/venv"
if [ ! -d "$VENV" ]; then
    # Fall back to repo-root venv
    VENV="$(dirname "$SCRIPT_DIR")/venv"
fi

[ ! -d "$VENV" ] && { echo "No venv found. Run ./setup.sh first."; exit 1; }
source "$VENV/bin/activate"

[ -f "$SCRIPT_DIR/.env" ] && { set -a; source "$SCRIPT_DIR/.env"; set +a; }
[ -z "${JWT_SECRET_KEY:-}" ] && export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

cd "$SCRIPT_DIR"
exec python3 main.py
