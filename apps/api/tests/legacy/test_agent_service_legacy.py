# apps/api/tests/test_agent_service_legacy.py

import pytest
from apps.api.services.agent_service import AgentService


# def test_agent_service():

@pytest.mark.skip(
    reason="Legacy AgentService replaced by nextgen AgentService"
)

@pytest.mark.anyio
async def test_agent_service():

    service = AgentService()

    # result = service.execute(
    #     prompt="Hello"
    # )
    result = await service.process_message(
        user_id="test-user",
        message="Hello",
    )

    assert result["status"] == "ok"