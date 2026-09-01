# apps/api/tests/nextgen/test_error_handler.py
#
# Verifies the single app-level exception handler (ADR-014): every
# AgentServiceError surfaces as HTTP 500 with a typed error body.
# raise_server_exceptions=False lets TestClient observe the handler's
# response instead of re-raising.

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routers.execute import agent_service

client = TestClient(app, raise_server_exceptions=False)


def offline_memory():
    mock_memory = AsyncMock()
    mock_memory.search.return_value = []
    mock_memory.save.return_value = None
    return mock_memory


def test_memory_search_failure_returns_typed_500():
    mock_memory = offline_memory()
    mock_memory.search.side_effect = RuntimeError("memory backend down")

    with patch.object(agent_service, "memory", mock_memory):
        response = client.post("/execute", json={"prompt": "Hello"})

    assert response.status_code == 500

    body = response.json()

    # The error body contract: exactly error_type and detail.
    assert set(body) == {"error_type", "detail"}
    assert body["error_type"] == "MemorySearchError"
    assert "memory backend down" in body["detail"]


def test_invalid_memory_data_returns_typed_500():
    mock_memory = offline_memory()
    mock_memory.search.return_value = 42  # no __len__ -> invalid

    with patch.object(agent_service, "memory", mock_memory):
        response = client.post("/execute", json={"prompt": "Hello"})

    assert response.status_code == 500
    assert response.json()["error_type"] == "InvalidMemoryDataError"


def test_none_llm_response_returns_typed_500():
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = None

    with (
        patch.object(agent_service, "memory", offline_memory()),
        patch.object(agent_service, "llm", mock_llm),
        patch(
            "apps.api.services.agent_service.get_llm_provider",
            return_value=mock_llm,
        ),
    ):
        response = client.post("/execute", json={"prompt": "Hello"})

    assert response.status_code == 500
    assert response.json()["error_type"] == "InvalidLLMResponseError"


def test_llm_provider_failure_returns_typed_500():
    mock_llm = AsyncMock()
    mock_llm.generate.side_effect = RuntimeError("provider exploded")

    with (
        patch.object(agent_service, "memory", offline_memory()),
        patch.object(agent_service, "llm", mock_llm),
        patch(
            "apps.api.services.agent_service.get_llm_provider",
            return_value=mock_llm,
        ),
    ):
        response = client.post("/execute", json={"prompt": "Hello"})

    assert response.status_code == 500

    body = response.json()
    assert body["error_type"] == "LLMProviderError"
    assert "provider exploded" in body["detail"]
