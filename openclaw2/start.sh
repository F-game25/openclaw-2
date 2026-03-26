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

# Ensure JWT_SECRET_KEY is stable across restarts by persisting it if needed
if [ -z "${JWT_SECRET_KEY:-}" ]; then
    SECRET_FILE="$SCRIPT_DIR/data/jwt_secret_key"
    if [ -f "$SECRET_FILE" ]; then
        JWT_SECRET_KEY="$(cat "$SECRET_FILE")"
        export JWT_SECRET_KEY
    else
        mkdir -p "$(dirname "$SECRET_FILE")"
        JWT_SECRET_KEY="$(python3 -c "import secrets; print(secrets.token_hex(32))")"
        printf '%s\n' "$JWT_SECRET_KEY" > "$SECRET_FILE"
        chmod 600 "$SECRET_FILE" 2>/dev/null || true
        export JWT_SECRET_KEY
        echo "Warning: JWT_SECRET_KEY was not set. Generated a new key and stored it at $SECRET_FILE" >&2
    fi
fi
cd "$SCRIPT_DIR"
exec python3 main.py
