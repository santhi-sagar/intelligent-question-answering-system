from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_ask_envelope():
    r = client.post("/api/ask", json={"question": "Hello?"})
    assert r.status_code == 200
    data = r.json()
    for key in ["answer_html", "citations", "followups", "query_rewrite", "safety_notes"]:
        assert key in data


