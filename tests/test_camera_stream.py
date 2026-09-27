from camera_test.camera_stream import CameraService, FrameBuffer


class FakeCamera:
    def __init__(self):
        self.configured = None
        self.recording = None
        self.stopped = False
        self.closed = False

    def create_video_configuration(self, **kwargs):
        return kwargs

    def configure(self, configuration):
        self.configured = configuration

    def start_recording(self, encoder, output):
        self.recording = (encoder, output)

    def stop_recording(self):
        self.stopped = True

    def close(self):
        self.closed = True


def test_frame_buffer_yields_new_frames():
    buffer = FrameBuffer()
    frames = buffer.frames()

    buffer.write(b"first")
    assert next(frames) == b"first"
    buffer.write(b"second")
    assert next(frames) == b"second"


def test_camera_service_configures_and_closes_camera():
    fake_camera = FakeCamera()
    service = CameraService(
        1280,
        720,
        30,
        camera_factory=lambda: fake_camera,
        encoder_factory=lambda: "encoder",
        output_factory=lambda buffer: ("output", buffer),
    )

    service.start()

    assert fake_camera.configured["main"] == {"size": (1280, 720)}
    assert fake_camera.configured["controls"] == {"FrameDurationLimits": (33333, 33333)}
    assert fake_camera.recording[0] == "encoder"
    assert service.diagnostics()["Status"] == "Streaming"
    assert service.diagnostics()["Stream"] == "1280 × 720 at 30 fps"

    service.stop()
    assert fake_camera.stopped is True
    assert fake_camera.closed is True
