# shutters

A simple Flask app to turn a monitor on/off when game streaming via Sunshine on KDE Wayland. Accessible from any device on your Tailscale network.

## Setup

### 1. Install dependencies

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't have it, then:

```bash
cd path/to/shutters
uv sync
```

This creates a `.venv` in the project directory automatically.

### 2. Find your monitor output name

```bash
kscreen-doctor -o
```

Look for your connected display — it will be something like `DP-1`, `DP-2`, `HDMI-A-1`, etc. Note the exact name.

### 3. Install the systemd user service

Run the install script, which detects your active monitor and project path automatically:

```bash
./install.sh
systemctl --user daemon-reload
systemctl --user enable --now shutters.service
```

Check it started:

```bash
systemctl --user status shutters.service
journalctl --user -u shutters.service -f
```

A `shutters.service.example` is also included if you prefer to configure the service manually.

### 5. Access the app

Open `http://<tailscale-ip>:5000` in any browser on your Tailscale network.

## Steam Deck shortcuts

Add non-Steam games in Steam with these launch options to create one-tap shortcuts:

- **Monitor Off**: `chromium --app=http://<tailscale-ip>:5000/off`
- **Monitor On**: `chromium --app=http://<tailscale-ip>:5000/on`

Each opens a minimal browser window, runs the command, and shows a confirmation page.

## Configuration (environment variables)

| Variable | Default | Description |
|---|---|---|
| `MONITOR_OUTPUT` | `DP-1` | Output name from `kscreen-doctor -o` |
| `PORT` | `5000` | Port to listen on |
| `HOST` | `0.0.0.0` | Address to bind (set to Tailscale IP to restrict access) |
| `WAYLAND_DISPLAY` | `/run/user/<uid>/wayland-0` | Wayland socket path (derived from current user at startup) |
| `DBUS_SESSION_BUS_ADDRESS` | `unix:path=/run/user/<uid>/bus` | D-Bus session socket path (derived from current user at startup) |
