# apps/api/tests/nextgen/test_observability_trace.py
#
# Covers the ADR-011 reserved observability fields now populated by the
# active pipeline: trace_id, timestamp, total_duration_ms, status,
# skill_selection, tools[] (per-tool detail), and llm.duration_ms/model.
#
# These tests are deterministic and hermetic: memory and the LLM are
# patched with AsyncMock, so no external provider or API call is made.
# The provider patches stay active across execute() because the LLM is
# re-resolved from the registry when a skill's backend differs from the
# configured default provider.

from contextlib import contextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from apps.api.providers.llm.mock import MockLLM
from apps.api.services.agent_service import AgentService
from apps.api.skills.registry import skills
from apps.api.skills.skill import Skill


@contextmanager
def patched_service(mock_memory, mock_llm):
    """Yield an AgentService whose memory and LLM providers are patched.

    The patches remain active for the whole context so execute() resolves
    the injected providers rather than the real registry.
    """
    with (
        patch(
            "apps.api.services.agent_service.get_memory_provider",
            return_value=mock_memory,
        ),
        patch(
            "apps.api.services.agent_service.get_llm_provider",
            return_value=mock_llm,
        ),
    ):
        yield AgentService()


@pytest.fixture
def mock_memory():
    memory = AsyncMock()
    memory.search.return_value = []
    memory.save.return_value = None
    return memory


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate.return_value = "generated response"
    return llm


# ---------------------------------------------------------------------------
# A. Basic trace metadata
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_trace_metadata(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        result = await service.execute(user_id="alice", prompt="Hello")

    trace = result["trace"]

    # trace_id exists and is non-empty.
    assert isinstance(trace["trace_id"], str)
    assert trace["trace_id"]

    # timestamp exists and is timezone-aware UTC.
    ts = trace["timestamp"]
    assert isinstance(ts, datetime)
    assert ts.tzinfo is not None
    assert ts.utcoffset() == UTC.utcoffset(None)

    # total_duration_ms exists and is non-negative.
    assert trace["total_duration_ms"] >= 0.0

    # status is "ok" on the success path.
    assert trace["status"] == "ok"


@pytest.mark.anyio
async def test_trace_ids_are_unique_per_execution(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        first = await service.execute(user_id="alice", prompt="Hello")
        second = await service.execute(user_id="alice", prompt="Hello")

    assert first["trace"]["trace_id"] != second["trace"]["trace_id"]


# ---------------------------------------------------------------------------
# B. Skill selection
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_skill_selection_matched_keyword(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        result = await service.execute(
            user_id="alice", prompt="Search for Python tutorials")

    selection = result["trace"]["skill_selection"]

    assert selection["selected_skill"] == "web_search"
    # available_skills mirrors the registry.
    assert selection["available_skills"] == [s.name for s in skills]
    # selection_reason reflects the existing keyword-match routing path.
    assert "matched keywords" in selection["selection_reason"]
    assert "search" in selection["selection_reason"]
    assert selection["selection_time_ms"] >= 0.0


@pytest.mark.anyio
async def test_skill_selection_fallback_reason(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        result = await service.execute(
            user_id="alice", prompt="What is the meaning of life?")

    selection = result["trace"]["skill_selection"]

    # Unmatched prompt falls back to skills[0] (echo); reason says so.
    assert selection["selected_skill"] == skills[0].name
    assert "no keyword match" in selection["selection_reason"]
    assert skills[0].name in selection["selection_reason"]


# ---------------------------------------------------------------------------
# C. Tools
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_tools_records_every_executed_tool_in_order(mock_memory, mock_llm):
    multi_tool_skill = Skill(
        name="multi",
        backend="mock",
        tools=["web_search", "summarize"],
        keywords=["multi"],
        priority=10,
    )

    with (
        patched_service(mock_memory, mock_llm) as service,
        patch(
            "apps.api.services.agent_service.select_skill",
            return_value=multi_tool_skill,
        ),
    ):
        result = await service.execute(
            user_id="alice", prompt="multi tool run")

    trace = result["trace"]
    tools_trace = trace["tools"]

    # Both registered tools are recorded, preserving execution order.
    assert [t["name"] for t in tools_trace] == ["web_search", "summarize"]
    assert [t["order"] for t in tools_trace] == [0, 1]

    for entry in tools_trace:
        assert entry["input"] == "multi tool run"
        assert isinstance(entry["output"], str)
        assert entry["duration_ms"] >= 0.0

    # Backward compatibility: `tool` remains the first executed tool.
    assert trace["tool"]["name"] == tools_trace[0]["name"]
    assert trace["tool"]["output"] == tools_trace[0]["output"]


@pytest.mark.anyio
async def test_tools_empty_when_skill_has_no_tools(mock_memory, mock_llm):
    no_tool_skill = Skill(
        name="no_tools",
        backend="mock",
        tools=[],
        keywords=["notools"],
        priority=10,
    )

    with (
        patched_service(mock_memory, mock_llm) as service,
        patch(
            "apps.api.services.agent_service.select_skill",
            return_value=no_tool_skill,
        ),
    ):
        result = await service.execute(user_id="alice", prompt="notools please")

    trace = result["trace"]
    assert trace["tools"] == []
    assert trace["tool"] is None


# ---------------------------------------------------------------------------
# D. LLM
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_llm_duration_populated_and_non_negative(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        result = await service.execute(user_id="alice", prompt="Hello")

    llm_trace = result["trace"]["llm"]

    assert llm_trace["duration_ms"] >= 0.0
    assert llm_trace["output"] == "generated response"
    # No fabricated token information.
    assert llm_trace.get("tokens_used") is None


@pytest.mark.anyio
async def test_llm_model_populated_when_provider_exposes_it(mock_memory):
    # An AsyncMock with a `model` attribute simulates a provider that
    # already exposes a model value (e.g. OllamaLLM) without changing the
    # LLMProvider contract.
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "response"
    mock_llm.model = "qwen3:8b"

    with patched_service(mock_memory, mock_llm) as service:
        result = await service.execute(user_id="alice", prompt="Hello")

    assert result["trace"]["llm"]["model"] == "qwen3:8b"


@pytest.mark.anyio
async def test_llm_model_none_when_provider_lacks_it(mock_memory):
    # The real MockLLM (the deterministic slice's provider) has no `model`
    # attribute, so the getattr default keeps the field None rather than
    # fabricating one.
    with patched_service(mock_memory, MockLLM()) as service:
        result = await service.execute(user_id="alice", prompt="Hello")

    assert result["trace"]["llm"]["model"] is None
    assert result["trace"]["llm"]["output"] == "echo: Hello"


# ---------------------------------------------------------------------------
# E. Backward compatibility / orchestration order
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_existing_trace_fields_preserved(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        result = await service.execute(user_id="alice", prompt="Hello")

    trace = result["trace"]

    # Previously populated fields remain intact.
    assert trace["context"] == {"user_id": "alice", "task": "Hello"}
    assert trace["skill"] == "echo"
    assert trace["tool"] == {
        "name": "echo",
        "output": "tool[echo] received: Hello",
    }
    assert trace["llm"]["provider"] == "mock"
    assert trace["llm"]["output"] == "generated response"
    assert trace["memory"]["memory_count"] == 0


@pytest.mark.anyio
async def test_orchestration_order_preserved(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        await service.execute(user_id="alice", prompt="Hello")

    # memory.search -> llm.generate -> memory.save sequence is unchanged.
    mock_memory.search.assert_awaited_once_with(user_id="alice", query="Hello")
    mock_llm.generate.assert_awaited_once()
    mock_memory.save.assert_awaited_once()


@pytest.mark.anyio
async def test_total_duration_is_non_negative(mock_memory, mock_llm):
    with patched_service(mock_memory, mock_llm) as service:
        result = await service.execute(user_id="alice", prompt="Search for agents")

    trace = result["trace"]

    parts = [
        trace["memory"]["search_duration_ms"],
        trace["memory"]["save_duration_ms"],
        trace["skill_selection"]["selection_time_ms"],
        trace["llm"]["duration_ms"],
    ]
    parts += [t["duration_ms"] for t in trace["tools"]]

    # Every measured sub-duration is non-negative, and so is the total.
    assert all(p >= 0.0 for p in parts)
    assert trace["total_duration_ms"] >= 0.0
