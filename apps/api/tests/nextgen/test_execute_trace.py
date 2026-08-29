# apps/api/tests/nextgen/test_execute_trace.py
#
# Verifies that /execute exposes the actual execution trace of the
# deterministic vertical slice:
#
#   Context -> Skill -> Tool -> LLM

import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routers.execute import agent_service


client = TestClient(app)


@pytest.fixture(autouse=True)
def offline_memory():
    """Keep the trace test hermetic (memory only; the LLM path runs
    through the real registry -> deterministic MockLLM)."""
    mock_memory = AsyncMock()
    mock_memory.search.return_value = []
    mock_memory.save.return_value = None

    with patch.object(agent_service, "memory", mock_memory):
        yield


def test_execute_exposes_context_skill_tool_llm_trace():
    response = client.post("/execute", json={"prompt": "Hello"})

    assert response.status_code == 200

    body = response.json()

    # Existing response fields and semantics are preserved.
    assert body["status"] == "ok"
    assert body["backend"] == "agent-service"
    assert body["prompt"] == "Hello"
    assert body["output"] == "echo: Hello"
    assert body["memory_count"] == 0

    trace = body["trace"]

    # Context: the actual ExecutionContext values.
    assert trace["context"] == {"user_id": "anonymous", "task": "Hello"}

    # Skill: the actually selected skill.
    assert trace["skill"] == "echo"

    # Tool: the actually executed tool name and output.
    assert trace["tool"] == {
        "name": "echo",
        "output": "tool[echo] received: Hello",
    }

    # LLM: the actually resolved provider and its actual output.
    assert trace["llm"] == {
        "provider": "mock",
        "output": "echo: Hello",
    }

    # The top-level output is the LLM output recorded in the trace.
    assert body["output"] == trace["llm"]["output"]
