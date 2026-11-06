"""Publish global workspace 1-8 states when Hyprland changes, never on a timer."""

import json
import os
import socket
import subprocess

WORKSPACE_COUNT = 8
EVENTS = (
    b"workspace", b"focusedmon", b"openwindow", b"closewindow", b"movewindow",
    b"createworkspace", b"destroyworkspace", b"moveworkspace",
    b"monitoradded", b"monitorremoved", b"configreloaded", b"activespecial",
)


def workspace_states(workspaces, active):
    dots = ["empty"] * WORKSPACE_COUNT
    for workspace in workspaces:
        number = workspace.get("id")
        if workspace.get("type") == "normal" and number in range(1, WORKSPACE_COUNT + 1):
            dots[number - 1] = "occupied" if workspace["windows"] > 0 else "empty"
    focused = active.get("id")
    if active.get("type") == "normal" and focused in range(1, WORKSPACE_COUNT + 1):
        dots[focused - 1] = "focused"
    return {"dots": dots}


def snapshot():
    raw = subprocess.check_output(
        ["hyprctl", "-j", "--batch", "workspaces;activeworkspace"],
        text=True, timeout=3,
    ).lstrip()
    workspaces, end = json.JSONDecoder().raw_decode(raw)
    active = json.loads(raw[end:])
    return workspace_states(workspaces, active)


def main():
    previous = None

    def publish(value):
        nonlocal previous
        if value != previous:
            print(json.dumps(value, separators=(",", ":")), flush=True)
            previous = value

    def refresh():
        try:
            publish(snapshot())
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            publish({"error": str(error)})

    socket_path = os.path.join(
        os.environ["XDG_RUNTIME_DIR"], "hypr",
        os.environ["HYPRLAND_INSTANCE_SIGNATURE"], ".socket2.sock",
    )
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as events:
            # Subscribe first so a change during the initial query cannot be lost.
            events.connect(socket_path)
            refresh()
            pending = b""
            while data := events.recv(65536):
                lines = (pending + data).split(b"\n")
                pending = lines.pop()
                if any(line.split(b">>", 1)[0].startswith(EVENTS) for line in lines):
                    refresh()
            publish({"error": "Hyprland workspace event stream closed"})
    except OSError as error:
        publish({"error": str(error)})


if __name__ == "__main__":
    main()
