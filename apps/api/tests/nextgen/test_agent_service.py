# apps/api/tests/nextgen/test_agent_service.py

import pytest

from apps.api.services.agent_service import AgentService


@pytest.mark.anyio
async def test_agent_service():

    service = AgentService()

    result = await service.execute(
        user_id="alice",
        prompt="Hello",
    )

    assert result["status"] == "ok"
    assert "output" in result
    assert isinstance(result["memory_count"], int)