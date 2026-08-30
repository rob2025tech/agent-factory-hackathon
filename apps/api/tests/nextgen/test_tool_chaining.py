# apps/api/tests/nextgen/test_tool_chaining.py

import pytest
from unittest.mock import patch

from apps.api.services.agent_service import AgentService
from apps.api.skills.skill import Skill


@pytest.mark.anyio
async def test_tool_chaining_execution():
    service = AgentService()

    test_skill = Skill(
        name="test",
        backend="mock",
        tools=["web_search", "summarize"],
        keywords=["test"],
        priority=10,
    )

    with (
        patch("apps.api.services.agent_service.select_skill",
              return_value=test_skill),
    ):
        result = await service.execute(prompt="Search for AI agents", user_id="test_user")

    trace = result["trace"]
    assert trace["tool"] is not None  # or however you extend the trace shape
