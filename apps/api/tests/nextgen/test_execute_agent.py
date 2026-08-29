# apps/api/tests/nextgen/test_execute_agent.py

from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_execute_agent_memory():

    response = client.post(
        "/execute",
        json={
            "user_id": "alice",
            "prompt": "I like pizza",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert "output" in body
    assert "memory_count" in body