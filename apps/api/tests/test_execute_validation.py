# apps/api/tests/test_execute_validation.py

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routers.execute import agent_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def offline_providers():
    """Keep validation tests hermetic (no local Ollama required)."""
    mock_memory = AsyncMock()
    mock_memory.search.return_value = []
    mock_memory.save.return_value = None

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "mock response"

    with (
        patch.object(agent_service, "memory", mock_memory),
        patch.object(agent_service, "llm", mock_llm),
        patch(
            "apps.api.services.agent_service.get_llm_provider",
            return_value=mock_llm,
        ),
    ):
        yield


def test_missing_prompt_returns_422():
    response = client.post("/execute", json={"backend": "ollama"})

    assert response.status_code == 422


def test_empty_body_returns_422():
    response = client.post("/execute", json={})

    assert response.status_code == 422


def test_valid_request_returns_full_response():
    response = client.post(
        "/execute",
        json={
            "prompt": "Hello",
            "backend": "ollama",
            "user_id": "alice",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["backend"] == "ollama"
    assert body["prompt"] == "Hello"
    assert body["output"] == "mock response"
    assert isinstance(body["memory_count"], int)


def test_extra_fields_are_ignored():
    response = client.post(
        "/execute",
        json={
            "prompt": "Hello",
            "unknown_field": "x",
        },
    )

    assert response.status_code == 200

    body = response.json()

    # Preserved behavior: omitted backend -> "agent-service".
    assert body["backend"] == "agent-service"


def test_non_string_prompt_returns_422():
    # Intended API contract: prompt must be a string.
    # Non-string prompts must be rejected, independent of any
    # incidental coercion behavior of the validation library.
    response = client.post("/execute", json={"prompt": 123})

    assert response.status_code == 422
