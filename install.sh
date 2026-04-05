#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/shutters.service"

# Detect active monitor
echo "Detecting monitors via kscreen-doctor..."
KSCREEN_OUTPUT=$(kscreen-doctor -o 2>&1)

# Prefer enabled+connected; fall back to just connected
MONITOR=$(echo "$KSCREEN_OUTPUT" | awk '/Output:/ && /enabled/ && /connected/ && !/disconnected/ {print $3; exit}')
if [[ -z "$MONITOR" ]]; then
    MONITOR=$(echo "$KSCREEN_OUTPUT" | awk '/Output:/ && /connected/ && !/disconnected/ {print $3; exit}')
fi

if [[ -z "$MONITOR" ]]; then
    echo "Error: no connected monitor found. Check 'kscreen-doctor -o'." >&2
    exit 1
fi

echo "Using monitor: $MONITOR"

UID_NUM=$(id -u)
mkdir -p "$SERVICE_DIR"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Shutters Monitor Control
After=network.target graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/app.py
Restart=on-failure
RestartSec=5

Environment=WAYLAND_DISPLAY=/run/user/$UID_NUM/wayland-0
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$UID_NUM/bus
Environment=MONITOR_OUTPUT=$MONITOR
Environment=PORT=5000
Environment=HOST=0.0.0.0

[Install]
WantedBy=default.target
EOF

echo "Written: $SERVICE_FILE"
echo ""
echo "Run to activate:"
echo "  systemctl --user daemon-reload"
echo "  systemctl --user enable --now shutters.service"
