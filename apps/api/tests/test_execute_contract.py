from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_execute_contract():

    response = client.post(
        "/execute",
        json={
            "backend": "ollama",
            "prompt": "Hello",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["backend"] == "ollama"
    assert body["prompt"] == "Hello"
