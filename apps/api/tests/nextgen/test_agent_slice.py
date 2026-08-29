# apps/api/tests/nextgen/test_agent_slice.py
#
# Deterministic vertical slice test:
#
#   AgentService -> ExecutionContext -> skill selection
#     -> registered tool execution -> deterministic mock LLM -> response

import pytest

from apps.api.providers.llm.mock import MockLLM
from apps.api.providers.llm.registry import get_llm_provider
from apps.api.services.agent_service import AgentService
from apps.api.skills.router import select as select_skill
from apps.api.tools.registry import tools


@pytest.mark.anyio
async def test_agent_factory_slice_is_deterministic():
    service = AgentService()

    result = await service.execute(
        user_id="alice",
        prompt="Hello slice",
    )

    assert result["status"] == "ok"

    # The deterministic mock LLM shapes the response from the prompt.
    assert result["output"] == "echo: Hello slice"

    # The same input always produces the same output.
    result_again = await service.execute(
        user_id="alice",
        prompt="Hello slice",
    )

    assert result_again["output"] == result["output"]


def test_slice_selects_echo_skill_with_registered_tool():
    skill = select_skill("anything")

    assert skill.name == "echo"
    assert skill.backend == "mock"
    assert skill.tools == ["echo"]

    # The skill's tool is registered and deterministic.
    assert tools["echo"].execute("hi") == "tool[echo] received: hi"

    # The skill's backend resolves to the deterministic mock LLM.
    assert isinstance(get_llm_provider(skill.backend), MockLLM)
