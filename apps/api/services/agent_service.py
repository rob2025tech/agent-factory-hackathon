# apps/api/services/agent_service.py

from apps.api.config.settings import settings

# from apps.api.providers.storage.registry import get_storage_provider
# from apps.api.providers.analytics.registry import get_analytics_provider
from apps.api.core.errors import (
    InvalidLLMResponseError,
    InvalidMemoryDataError,
    LLMProviderError,
    MemorySaveError,
    MemorySearchError,
    ProviderInitError,
)
from apps.api.core.execution_context import ExecutionContext
from apps.api.providers.llm.registry import get_llm_provider
from apps.api.providers.memory.registry import get_memory_provider
from apps.api.skills.router import select as select_skill
from apps.api.tools.registry import tools


class AgentService:

    def __init__(self):
        try:
            self.memory = get_memory_provider(settings.memory_provider)
        except Exception as e:
            raise ProviderInitError(
                f"Failed to initialize memory provider: {e}") from e

        try:
            self.llm = get_llm_provider(settings.llm_provider)
        except Exception as e:
            raise ProviderInitError(
                f"Failed to initialize LLM provider: {e}") from e

        # self.storage = get_storage_provider(
        #     settings.storage_provider
        # )
        # self.analytics = get_analytics_provider(
        #     settings.analytics_provider
        # )

    async def execute(
        self,
        user_id: str,
        prompt: str,
    ):
        # 1. Search memory
        try:
            memories = await self.memory.search(
                user_id=user_id,
                query=prompt,
            )
        except Exception as e:
            raise MemorySearchError(
                f"Memory search failed for user '{user_id}': {e}") from e

        # 2. Validate memories is iterable
        if not hasattr(memories, '__len__'):
            raise InvalidMemoryDataError(
                f"Memory search returned non-iterable type: {type(memories).__name__}"
            )

        # 3. Generate LLM response
        #
        # Deterministic agent factory slice:
        #
        #   ExecutionContext -> Skill selection -> Tool execution
        #     -> LLM provider chosen from the selected skill's backend.
        #
        # The memory.search() / llm.generate() / memory.save() contract
        # below is intentionally unchanged.
        context = ExecutionContext(
            user_id=user_id,
            task=prompt,
        )

        skill = select_skill(prompt)

        context = context.with_metadata(skill=skill.name)

        # Run the skill's registered tools (deterministic).
        tool_outputs = {}
        for tool_name in skill.tools:
            tool = tools.get(tool_name)
            if tool is not None:
                tool_outputs[tool_name] = tool.execute(prompt)

        if tool_outputs:
            context = context.with_metadata(tool_outputs=tool_outputs)

        # Resolve the LLM for the selected skill's backend.
        # If the backend matches the configured default provider, reuse the
        # provider constructed at init so injected/patched providers apply.
        if skill.backend == settings.llm_provider:
            llm = self.llm
        else:
            llm = get_llm_provider(skill.backend)

        try:
            response = await llm.generate(
                prompt=prompt,
                memories=memories,
            )
        except Exception as e:
            raise LLMProviderError(f"LLM generation failed: {e}") from e

        # 4. Validate LLM response - DECISION: Treat None as error
        # Trade-off: This is a hard fail. If you want graceful degradation,
        # change this to allow None and handle it downstream.
        if response is None:
            raise InvalidLLMResponseError("LLM returned None")

        # Observable execution trace, assembled from the actual values
        # produced by this execution (context, selected skill, executed
        # tool, resolved provider, and LLM output).
        first_tool = next(iter(tool_outputs.items()), None)

        trace = {
            "context": {
                "user_id": context.user_id,
                "task": context.task,
            },
            "skill": skill.name,
            "tool": (
                {
                    "name": first_tool[0],
                    "output": first_tool[1],
                }
                if first_tool is not None
                else None
            ),
            "llm": {
                "provider": skill.backend,
                "output": response,
            },
        }

        # 5. Save to memory
        try:
            await self.memory.save(
                user_id=user_id,
                data={
                    "prompt": prompt,
                    "response": response,
                },
            )
        except Exception as e:
            raise MemorySaveError(
                f"Failed to save conversation for user '{user_id}': {e}") from e

        # 6. (Commented out) Storage and analytics
        # await self.storage.save_conversation(
        #     user_id=user_id,
        #     prompt=prompt,
        #     response=response,
        # )
        # await self.analytics.record_request(
        #     provider=settings.llm_provider,
        #     prompt=prompt,
        #     response=response,
        # )

        return {
            "status": "ok",
            "output": response,
            "memory_count": len(memories),
            "trace": trace,
        }
