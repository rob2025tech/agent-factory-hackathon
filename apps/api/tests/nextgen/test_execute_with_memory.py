# apps/api/tests/nextgen/test_execute_with_memory.py# apps/api/tests/nextgen/test_execute_with_memory.py

import pytest

from apps.api.services.agent_service import AgentService

@pytest.mark.skip(reason="Awaiting semantic memory implementation")
@pytest.mark.anyio
async def test_execute_with_memory():

    service = AgentService()

    await service.execute(
        user_id="alice",
        prompt="My favorite language is Python.",
    )

    result = await service.execute(
        user_id="alice",
        prompt="What is my favorite language?",
    )

    assert result["status"] == "ok"

    assert result["memory_count"] >= 1

    assert isinstance(
        result["output"],
        str,
    )

    assert len(result["output"]) > 0