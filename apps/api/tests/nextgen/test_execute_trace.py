# apps/api/tests/nextgen/test_execute_trace.py
#
# Verifies that /execute exposes the actual execution trace of the
# deterministic vertical slice:
#
#   Context -> Skill -> Tool -> LLM

from unittest.mock import AsyncMock, patch

import pytest
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
    assert trace["llm"]["provider"] == "mock"
    assert trace["llm"]["output"] == "echo: Hello"

    # The top-level output is the LLM output recorded in the trace.
    assert body["output"] == trace["llm"]["output"]


def test_execute_exposes_observability_trace_fields():
    """The ADR-011 reserved fields survive Pydantic validation and JSON
    serialization end-to-end through /execute."""
    response = client.post("/execute", json={"prompt": "Search for agents"})

    assert response.status_code == 200

    trace = response.json()["trace"]

    # Metadata: trace_id, timezone-aware UTC timestamp, status, total time.
    assert trace["trace_id"]
    assert trace["timestamp"].endswith(("Z", "+00:00"))
    assert trace["status"] == "ok"
    assert trace["total_duration_ms"] >= 0.0

    # Skill selection detail.
    selection = trace["skill_selection"]
    assert selection["selected_skill"] == trace["skill"] == "web_search"
    assert "echo" in selection["available_skills"]
    assert selection["selection_reason"]
    assert selection["selection_time_ms"] >= 0.0

    # Per-tool detail; `tool` remains the first executed tool.
    names = [t["name"] for t in trace["tools"]]
    assert names == ["web_search", "summarize"]
    assert [t["order"] for t in trace["tools"]] == [0, 1]
    for entry in trace["tools"]:
        assert entry["input"] == "Search for agents"
        assert entry["duration_ms"] >= 0.0
    assert trace["tool"]["name"] == trace["tools"][0]["name"]

    # LLM timing is populated; token counts are not fabricated.
    assert trace["llm"]["duration_ms"] >= 0.0
    assert trace["llm"]["tokens_used"] is None
