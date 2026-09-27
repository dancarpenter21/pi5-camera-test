# Camera Module 3 Test

Serve a live MJPEG preview from a Raspberry Pi Camera Module 3 on a Raspberry
Pi 5. The server listens on the local network by default, so any device on the
same LAN can open the preview in a browser.

## Prerequisites

Raspberry Pi OS must detect the camera and provide Picamera2. Confirm this with:

```bash
rpicam-hello --list-cameras
```

The project uses `uv`. Picamera2 is supplied by Raspberry Pi OS because it
depends on the native camera stack, so create the project environment with
access to the OS site packages:

```bash
uv venv --system-site-packages
uv sync --group dev
```

## Run

Start the server from this directory:

```bash
uv run camera-stream
```

Open `http://<pi-lan-address>:8000/` from a device on the same network. The
default stream is 1280x720 at 30 fps.

Use `--host`, `--port`, `--width`, `--height`, and `--fps` to change the
network binding or capture settings. For example:

```bash
uv run camera-stream --port 8080 --width 1920 --height 1080 --fps 30
```

Stop the foreground server with `Ctrl+C`.

## Troubleshooting

If startup reports that the camera could not be opened, first rerun
`rpicam-hello --list-cameras`, then check the camera ribbon cable and confirm
that no other process is using the camera.
