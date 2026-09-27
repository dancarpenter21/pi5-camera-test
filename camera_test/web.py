"""Flask routes for the packaged live camera preview."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from flask import Flask, Response, render_template


class FrameSource(Protocol):
    def frames(self) -> Iterable[bytes]: ...


class DiagnosticsSource(Protocol):
    def diagnostics(self) -> dict[str, str]: ...


def create_app(frame_source: FrameSource, diagnostics_source: DiagnosticsSource | None = None) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        diagnostics = (
            diagnostics_source.diagnostics()
            if diagnostics_source is not None
            else {"Status": "Streaming"}
        )
        return render_template("index.html", diagnostics=diagnostics)

    @app.get("/stream.mjpg")
    def stream() -> Response:
        def multipart_frames() -> Iterable[bytes]:
            for frame in frame_source.frames():
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

        return Response(
            multipart_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    return app
