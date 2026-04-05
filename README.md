# shutters

A simple Flask app to turn a monitor on/off when game streaming via Sunshine on KDE Wayland. Accessible from any device on your Tailscale network.

## Setup

### 1. Install Flask

On Bazzite (immutable Fedora), use `pipx` or a venv:

```bash
python3 -m venv ~/Projects/shutters/.venv
source ~/Projects/shutters/.venv/bin/activate
pip install flask
```

Then update the `ExecStart` line in the service file to use the venv Python:

```ini
ExecStart=%h/Projects/shutters/.venv/bin/python %h/Projects/shutters/app.py
```

### 2. Find your monitor output name

```bash
kscreen-doctor -o
```

Look for your connected display — it will be something like `DP-1`, `DP-2`, `HDMI-A-1`, etc. Note the exact name.

### 3. Configure the output name

Edit `monitor-control.service` and set `MONITOR_OUTPUT` to the name you found:

```ini
Environment=MONITOR_OUTPUT=DP-1
```

Or export it in your shell before running manually:

```bash
MONITOR_OUTPUT=DP-1 python app.py
```

### 4. Install the systemd user service

```bash
mkdir -p ~/.config/systemd/user
cp ~/Projects/shutters/monitor-control.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now monitor-control.service
```

Check it started:

```bash
systemctl --user status monitor-control.service
journalctl --user -u monitor-control.service -f
```

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
| `WAYLAND_DISPLAY` | `/run/user/1000/wayland-0` | Wayland socket path |
| `DBUS_SESSION_BUS_ADDRESS` | `unix:path=/run/user/1000/bus` | D-Bus session socket path |
