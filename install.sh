#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/shutters.service"

# Detect active monitor
echo "Detecting monitors via kscreen-doctor..."
KSCREEN_OUTPUT=$(kscreen-doctor -o 2>&1)

# Collect all connected monitors
ALL_MONITORS=$(echo "$KSCREEN_OUTPUT" | awk '/Output:/ && /connected/ && !/disconnected/ {print $3}')

if [[ -z "$ALL_MONITORS" ]]; then
    echo "Error: no connected monitor found. Check 'kscreen-doctor -o'." >&2
    exit 1
fi

MONITOR=$(echo "$ALL_MONITORS" | head -1)
MONITOR_COUNT=$(echo "$ALL_MONITORS" | wc -l)

if [[ "$MONITOR_COUNT" -gt 1 ]]; then
    echo "Multiple connected monitors detected:"
    echo "$ALL_MONITORS" | sed 's/^/  /'
    echo "Using: $MONITOR"
    echo "If this is wrong, edit MONITOR_OUTPUT in $HOME/.config/systemd/user/shutters.service"
    echo ""
else
    echo "Using monitor: $MONITOR"
fi

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
