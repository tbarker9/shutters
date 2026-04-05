import subprocess
import os
from flask import Flask

app = Flask(__name__)

# Configure your monitor output name here, or set MONITOR_OUTPUT env var
MONITOR_OUTPUT = os.environ.get("MONITOR_OUTPUT", "DP-1")
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")

_uid = os.getuid()
KSCREEN_ENV = {
    **os.environ,
    "WAYLAND_DISPLAY": os.environ.get("WAYLAND_DISPLAY", f"/run/user/{_uid}/wayland-0"),
    "DBUS_SESSION_BUS_ADDRESS": os.environ.get(
        "DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{_uid}/bus"
    ),
}


def run_kscreen(action: str):
    """Run kscreen-doctor to enable or disable the monitor. action: 'enable' or 'disable'"""
    cmd = ["kscreen-doctor", f"output.{MONITOR_OUTPUT}.{action}"]
    result = subprocess.run(cmd, env=KSCREEN_ENV, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Monitor Control</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: #1a1a2e;
      font-family: sans-serif;
      gap: 2rem;
      padding: 2rem;
    }}
    h1 {{ color: #eee; font-size: 1.5rem; }}
    .buttons {{ display: flex; gap: 1.5rem; flex-wrap: wrap; justify-content: center; }}
    a.btn {{
      display: inline-block;
      padding: 1.2rem 3rem;
      font-size: 1.4rem;
      font-weight: bold;
      border-radius: 0.75rem;
      text-decoration: none;
      cursor: pointer;
    }}
    .btn-off  {{ background: #c0392b; color: #fff; }}
    .btn-on   {{ background: #27ae60; color: #fff; }}
    .btn-off:hover  {{ background: #e74c3c; }}
    .btn-on:hover   {{ background: #2ecc71; }}
    .status {{ color: #aaa; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Monitor Control</h1>
  <div class="buttons">
    <a class="btn btn-off" href="/off">Monitor Off</a>
    <a class="btn btn-on"  href="/on">Monitor On</a>
  </div>
  {status}
</body>
</html>"""

ACTION_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Monitor {title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: #1a1a2e;
      font-family: sans-serif;
      gap: 1.5rem;
      padding: 2rem;
      text-align: center;
    }}
    h1 {{ color: {color}; font-size: 2rem; }}
    p  {{ color: #aaa; font-size: 0.9rem; max-width: 30rem; }}
    a  {{ color: #7fa7d8; font-size: 1rem; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>{message}</h1>
  {detail}
  <a href="/">Back</a>
</body>
</html>"""


@app.route("/")
def index():
    return INDEX_HTML.format(status=""), 200


@app.route("/off")
def monitor_off():
    ok, output = run_kscreen("disable")
    if ok:
        return ACTION_HTML.format(
            title="Off",
            color="#e74c3c",
            message="Monitor Off",
            detail="<p>Display disabled successfully.</p>",
        ), 200
    return ACTION_HTML.format(
        title="Error",
        color="#e67e22",
        message="Command Failed",
        detail=f"<p>{output or 'Unknown error'}</p>",
    ), 500


@app.route("/on")
def monitor_on():
    ok, output = run_kscreen("enable")
    if ok:
        return ACTION_HTML.format(
            title="On",
            color="#2ecc71",
            message="Monitor On",
            detail="<p>Display enabled successfully.</p>",
        ), 200
    return ACTION_HTML.format(
        title="Error",
        color="#e67e22",
        message="Command Failed",
        detail=f"<p>{output or 'Unknown error'}</p>",
    ), 500


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
