"""Command-line entry point for the Camera Module 3 preview server."""

from __future__ import annotations

import argparse
import logging

from camera_test.camera_stream import CameraService
from camera_test.web import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a Camera Module 3 MJPEG preview.")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to bind (default: 0.0.0.0).")
    parser.add_argument("--port", default=8000, type=int, help="TCP port to bind (default: 8000).")
    parser.add_argument("--width", default=1280, type=int, help="Stream width in pixels (default: 1280).")
    parser.add_argument("--height", default=720, type=int, help="Stream height in pixels (default: 720).")
    parser.add_argument("--fps", default=30, type=int, help="Target frame rate (default: 30).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.width <= 0 or args.height <= 0 or args.fps <= 0 or not 1 <= args.port <= 65535:
        raise SystemExit("width, height, fps, and port must be positive; port must be at most 65535")

    camera = CameraService(args.width, args.height, args.fps)
    try:
        camera.start()
    except Exception as error:
        logging.error("Could not start the camera: %s", error)
        logging.error("Check the connection with: rpicam-hello --list-cameras")
        return 1

    app = create_app(camera.buffer, camera)
    try:
        app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)
    finally:
        camera.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
