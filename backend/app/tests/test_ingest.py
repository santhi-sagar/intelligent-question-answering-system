from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_ingest_file_unsupported():
    files = {"file": ("test.bin", b"data", "application/octet-stream")}
    r = client.post("/api/ingest/file", files=files)
    assert r.status_code == 400


