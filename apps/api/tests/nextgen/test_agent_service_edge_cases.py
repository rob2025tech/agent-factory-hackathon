# apps/api/tests/nextgen/test_agent_service_edge_cases.py

import pytest
from unittest.mock import AsyncMock, patch

from apps.api.services.agent_service import AgentService
from apps.api.core.errors import InvalidMemoryDataError, InvalidLLMResponseError


@pytest.fixture
def mock_memory():
    return AsyncMock()


@pytest.fixture
def mock_llm():
    return AsyncMock()


@pytest.fixture
def agent_service_with_mocks(mock_memory, mock_llm):
    with patch(
        "apps.api.services.agent_service.get_memory_provider",
        return_value=mock_memory,
    ), patch(
        "apps.api.services.agent_service.get_llm_provider",
        return_value=mock_llm,
    ):
        service = AgentService()
        yield service, mock_memory, mock_llm


# ============================================================================
# EDGE CASE: memory.search() returns empty list
# ============================================================================

@pytest.mark.anyio
async def test_handles_empty_search_results(agent_service_with_mocks):
    """
    What happens when memory.search() returns an empty list?

    Expected: Should still work with memory_count=0, llm.generate() receives
    empty list, memory.save() still called with the response.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    # Setup: search returns empty list
    mock_memory.search.return_value = []
    mock_llm.generate.return_value = "Response with no context"

    result = await service.execute(user_id="alice", prompt="Hello")

    # Verify the flow still works
    mock_memory.search.assert_awaited_once_with(
        user_id="alice",
        query="Hello"
    )
    mock_llm.generate.assert_awaited_once_with(
        prompt="Hello",
        memories=[]  # Empty list passed through
    )
    mock_memory.save.assert_awaited_once_with(
        user_id="alice",
        data={
            "prompt": "Hello",
            "response": "Response with no context"
        }
    )
    assert result["memory_count"] == 0
    assert result["output"] == "Response with no context"
    assert result["status"] == "ok"


# ============================================================================
# EDGE CASE: memory.search() raises an exception
# ============================================================================

@pytest.mark.anyio
async def test_raises_when_memory_search_fails(agent_service_with_mocks):
    """
    What happens when memory.search() raises an exception?

    Expected: The exception should propagate up. No further calls should be made.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    # Setup: search raises
    mock_memory.search.side_effect = Exception("Database connection failed")

    with pytest.raises(Exception, match="Database connection failed"):
        await service.execute(user_id="alice", prompt="Hello")

    # Verify no further calls were made
    mock_llm.generate.assert_not_awaited()
    mock_memory.save.assert_not_awaited()


@pytest.mark.anyio
async def test_raises_when_memory_search_returns_non_iterable(agent_service_with_mocks):
    """
    What happens when memory.search() returns something that breaks len()?

    Expected: InvalidMemoryDataError should be raised, per the current
    AgentService contract for invalid provider results.
    """
    service, mock_memory, _ = agent_service_with_mocks

    # Setup: search returns something that breaks len()
    mock_memory.search.return_value = None  # None has no len()

    with pytest.raises(InvalidMemoryDataError):
        await service.execute(user_id="alice", prompt="Hello")


# ============================================================================
# EDGE CASE: llm.generate() returns None
# ============================================================================

@pytest.mark.anyio
async def test_raises_when_llm_generate_returns_none(agent_service_with_mocks):
    """
    What happens when llm.generate() returns None?

    Expected: InvalidLLMResponseError should be raised, per the current
    AgentService contract for invalid provider results. memory.save()
    should NOT be called.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    # Setup: search returns something, generate returns None
    mock_memory.search.return_value = ["memory1"]
    mock_llm.generate.return_value = None

    with pytest.raises(InvalidLLMResponseError):
        await service.execute(user_id="alice", prompt="Hello")

    mock_llm.generate.assert_awaited_once_with(
        prompt="Hello",
        memories=["memory1"]
    )
    mock_memory.save.assert_not_awaited()


@pytest.mark.anyio
async def test_handles_llm_generate_returns_empty_string(agent_service_with_mocks):
    """
    What happens when llm.generate() returns empty string?

    Expected: Should work, output is empty string.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    mock_memory.search.return_value = ["memory1"]
    mock_llm.generate.return_value = ""

    result = await service.execute(user_id="alice", prompt="Hello")

    assert result["output"] == ""
    assert result["status"] == "ok"
    mock_memory.save.assert_awaited_once_with(
        user_id="alice",
        data={
            "prompt": "Hello",
            "response": ""
        }
    )


# ============================================================================
# EDGE CASE: llm.generate() raises an exception
# ============================================================================

@pytest.mark.anyio
async def test_raises_when_llm_generate_fails(agent_service_with_mocks):
    """
    What happens when llm.generate() raises an exception?

    Expected: Exception should propagate. memory.save() should NOT be called.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    mock_memory.search.return_value = ["memory1"]
    mock_llm.generate.side_effect = Exception("LLM API rate limit exceeded")

    with pytest.raises(Exception, match="LLM API rate limit exceeded"):
        await service.execute(user_id="alice", prompt="Hello")

    # Verify search was called, but save was not
    mock_memory.search.assert_awaited_once()
    mock_memory.save.assert_not_awaited()


# ============================================================================
# EDGE CASE: memory.save() fails
# ============================================================================

@pytest.mark.anyio
async def test_raises_when_memory_save_fails(agent_service_with_mocks):
    """
    What happens when memory.save() raises an exception?

    Expected: Exception should propagate. The response was already generated
    but couldn't be saved.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    mock_memory.search.return_value = ["memory1"]
    mock_llm.generate.return_value = "Generated response"
    mock_memory.save.side_effect = Exception("Failed to save to memory")

    with pytest.raises(Exception, match="Failed to save to memory"):
        await service.execute(user_id="alice", prompt="Hello")

    # Verify search and generate were called, but the exception came from save
    mock_memory.search.assert_awaited_once()
    mock_llm.generate.assert_awaited_once()
    mock_memory.save.assert_awaited_once()


# ============================================================================
# EDGE CASE: Multiple concurrent calls (isolation)
# ============================================================================

@pytest.mark.anyio
async def test_calls_are_isolated_between_requests(agent_service_with_mocks):
    """
    Verify that each execute() call is independent.

    This matters because the service doesn't maintain state between calls.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    # Setup
    mock_memory.search.return_value = ["memory1"]
    mock_llm.generate.return_value = "Response 1"

    # First call
    result1 = await service.execute(user_id="alice", prompt="Hello")
    assert result1["output"] == "Response 1"

    # Second call with different values
    mock_memory.search.return_value = ["memory2", "memory3"]
    mock_llm.generate.return_value = "Response 2"

    result2 = await service.execute(user_id="bob", prompt="Hi")
    assert result2["output"] == "Response 2"
    assert result2["memory_count"] == 2

    # Verify the mocks were called correctly for each
    assert mock_memory.search.call_count == 2
    mock_memory.search.assert_any_call(user_id="alice", query="Hello")
    mock_memory.search.assert_any_call(user_id="bob", query="Hi")

    assert mock_llm.generate.call_count == 2
    mock_llm.generate.assert_any_call(prompt="Hello", memories=["memory1"])
    mock_llm.generate.assert_any_call(prompt="Hi", memories=["memory2", "memory3"])


# ============================================================================
# EDGE CASE: Large memory list
# ============================================================================

@pytest.mark.anyio
async def test_handles_large_number_of_memories(agent_service_with_mocks):
    """
    What happens when search returns many memories?

    Expected: Should handle large lists without issues.
    """
    service, mock_memory, mock_llm = agent_service_with_mocks

    # Setup: 1000 memories
    large_memory_list = [f"memory_{i}" for i in range(1000)]
    mock_memory.search.return_value = large_memory_list
    mock_llm.generate.return_value = "Response from large context"

    result = await service.execute(user_id="alice", prompt="Hello")

    mock_llm.generate.assert_awaited_once_with(
        prompt="Hello",
        memories=large_memory_list
    )
    assert result["memory_count"] == 1000
    assert result["output"] == "Response from large context"
