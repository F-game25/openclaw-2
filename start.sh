#!/bin/bash
# Start script — AI Employee + OpenClaw 2

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW2_DIR="$REPO_DIR/openclaw2"

echo "================================================"
echo "AI Employee + OpenClaw 2"
echo "================================================"

# ── Virtual environment check ─────────────────────────────────────────────────
if [ ! -d "$REPO_DIR/venv" ]; then
    echo "Error: virtual environment not found. Run ./setup.sh first."
    exit 1
fi

source "$REPO_DIR/venv/bin/activate"
export PATH="$REPO_DIR/venv/bin:$PATH"

# ── Load OpenClaw 2 .env ─────────────────────────────────────────────────────
if [ -f "$OPENCLAW2_DIR/.env" ]; then
    set -a; source "$OPENCLAW2_DIR/.env"; set +a
fi

# Auto-generate JWT secret for the session if none set
if [ -z "${JWT_SECRET_KEY:-}" ]; then
    export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "⚠️  No JWT_SECRET_KEY set — generated one for this session."
    echo "   Add to openclaw2/.env:  JWT_SECRET_KEY=$JWT_SECRET_KEY"
    echo ""
fi

# ── Start OpenClaw 2 API server ───────────────────────────────────────────────
echo "Starting OpenClaw 2 API server (http://127.0.0.1:8000)..."
mkdir -p "$OPENCLAW2_DIR/logs"
cd "$OPENCLAW2_DIR"
nohup python3 main.py >> "$OPENCLAW2_DIR/logs/openclaw.log" 2>&1 &
OPENCLAW_PID=$!
echo "$OPENCLAW_PID" > "$REPO_DIR/run/openclaw.pid"
echo "✓ OpenClaw 2 started (pid=$OPENCLAW_PID)"
cd "$REPO_DIR"

# ── Start AI Employee bots ────────────────────────────────────────────────────
export AI_HOME="$REPO_DIR"
mkdir -p "$REPO_DIR/run" "$REPO_DIR/state"

AI_EMPLOYEE_BIN="$REPO_DIR/runtime/bin/ai-employee"
if [ -x "$AI_EMPLOYEE_BIN" ]; then
    echo "Starting AI Employee bots..."
    "$AI_EMPLOYEE_BIN" start --all >> "$REPO_DIR/logs/startup.log" 2>&1 || true
    echo "✓ AI Employee bots started (Problem Solver UI: http://127.0.0.1:8787)"
else
    echo "⚠️  AI Employee bin not found — skipping bots"
fi

echo ""
echo "================================================"
echo "All services running"
echo "================================================"
echo "  OpenClaw 2 API:    http://127.0.0.1:8000"
echo "  Problem Solver UI: http://127.0.0.1:8787"
echo "  Logs: openclaw2/logs/  |  logs/"
echo ""
echo "Press Ctrl+C to stop all services."
echo ""

cleanup() {
    echo "Stopping all services..."
    [ -x "$AI_EMPLOYEE_BIN" ] && "$AI_EMPLOYEE_BIN" stop --all >/dev/null 2>&1 || true
    [ -f "$REPO_DIR/run/openclaw.pid" ] && kill "$(cat "$REPO_DIR/run/openclaw.pid")" 2>/dev/null || true
    rm -f "$REPO_DIR/run/openclaw.pid"
    echo "✓ Stopped."
}
trap cleanup EXIT INT TERM
wait $OPENCLAW_PID 2>/dev/null || true
