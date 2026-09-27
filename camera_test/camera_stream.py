"""Camera capture and MJPEG frame sharing for the application package."""

from __future__ import annotations

import io
import threading
from collections.abc import Iterator
from typing import Any, Callable


class FrameBuffer(io.BufferedIOBase):
    """A file-like output that retains the newest JPEG frame for all viewers."""

    def __init__(self) -> None:
        super().__init__()
        self._condition = threading.Condition()
        self._frame = b""
        self._sequence = 0

    def writable(self) -> bool:
        return True

    def write(self, frame: bytes) -> int:
        with self._condition:
            self._frame = bytes(frame)
            self._sequence += 1
            self._condition.notify_all()
        return len(frame)

    def frames(self) -> Iterator[bytes]:
        """Yield each new frame, blocking until the camera produces one."""
        sequence = 0
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._sequence != sequence)
                sequence = self._sequence
                frame = self._frame
            yield frame


class CameraService:
    """Owns the single physical camera and its MJPEG encoder."""

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        *,
        camera_factory: Callable[[], Any] | None = None,
        encoder_factory: Callable[[], Any] | None = None,
        output_factory: Callable[[FrameBuffer], Any] | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self.buffer = FrameBuffer()
        self._camera_factory = camera_factory
        self._encoder_factory = encoder_factory
        self._output_factory = output_factory
        self._camera: Any | None = None
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        if self._camera_factory is None or self._encoder_factory is None or self._output_factory is None:
            from picamera2 import Picamera2
            from picamera2.encoders import MJPEGEncoder
            from picamera2.outputs import FileOutput

            self._camera_factory = Picamera2
            self._encoder_factory = MJPEGEncoder
            self._output_factory = FileOutput

        camera = self._camera_factory()
        frame_duration_us = 1_000_000 // self.fps
        configuration = camera.create_video_configuration(
            main={"size": (self.width, self.height)},
            controls={"FrameDurationLimits": (frame_duration_us, frame_duration_us)},
        )
        try:
            camera.configure(configuration)
            camera.start_recording(self._encoder_factory(), self._output_factory(self.buffer))
        except Exception:
            close = getattr(camera, "close", None)
            if close is not None:
                close()
            raise

        self._camera = camera
        self._started = True

    def stop(self) -> None:
        if not self._started or self._camera is None:
            return
        try:
            self._camera.stop_recording()
        finally:
            self._camera.close()
            self._camera = None
            self._started = False

    def diagnostics(self) -> dict[str, str]:
        """Return safe, human-readable status for the preview page."""
        details = {
            "Status": "Streaming" if self._started else "Stopped",
            "Stream": f"{self.width} × {self.height} at {self.fps} fps",
        }
        if self._camera is not None:
            properties = getattr(self._camera, "camera_properties", {})
            model = properties.get("Model") or properties.get("CameraModel")
            if model:
                details["Camera"] = str(model)
        return details
