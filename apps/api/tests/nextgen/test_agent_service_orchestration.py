# apps/api/tests/nextgen/test_agent_service_orchestration.py

import pytest
from unittest.mock import AsyncMock, patch

from apps.api.services.agent_service import AgentService


@pytest.mark.anyio
async def test_agent_service_orchestration():

    fake_memories = ["memory_one", "memory_two", "memory_three"]
    fake_response = "This is the LLM response"

    mock_memory = AsyncMock()
    mock_memory.search.return_value = fake_memories
    mock_memory.save.return_value = None

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = fake_response

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
        service = AgentService()

        result = await service.execute(
            user_id="alice",
            prompt="Hello",
        )

    # 1. memory.search() receives the correct user_id and prompt/query.
    mock_memory.search.assert_awaited_once_with(
        user_id="alice",
        query="Hello",
    )

    # 2. The memories returned by memory.search() are passed to llm.generate().
    # 3. llm.generate() receives the original prompt.
    mock_llm.generate.assert_awaited_once_with(
        prompt="Hello",
        memories=fake_memories,
    )

    # 4. memory.save() receives the original user_id.
    # 5. memory.save() receives the original prompt and the exact LLM response.
    mock_memory.save.assert_awaited_once_with(
        user_id="alice",
        data={
            "prompt": "Hello",
            "response": fake_response,
        },
    )

    # 6. The returned status indicates successful execution.
    assert result["status"] == "ok"

    # 7. memory_count equals len(memories).
    assert result["memory_count"] == len(fake_memories)

    # 8. The returned output equals the exact value returned by the mocked LLM.
    assert result["output"] == fake_response
