from camera_test.web import create_app


class Frames:
    def frames(self):
        yield b"jpeg-data"


def test_index_renders_live_preview():
    client = create_app(Frames()).test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"/stream.mjpg" in response.data
    assert b"Camera diagnostics" in response.data
    assert b"Streaming" in response.data


def test_stream_is_multipart_jpeg():
    client = create_app(Frames()).test_client()

    response = client.get("/stream.mjpg", buffered=False)

    assert response.status_code == 200
    assert response.content_type == "multipart/x-mixed-replace; boundary=frame"
    assert next(response.response) == b"--frame\r\nContent-Type: image/jpeg\r\n\r\njpeg-data\r\n"
