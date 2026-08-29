from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_execute_ollama():
    response = client.post(
        "/execute",
        json={"backend": "ollama", "prompt": "Say hello in one word."},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["backend"] == "ollama"
    assert body["prompt"] == "Say hello in one word."
    assert "output" in body
