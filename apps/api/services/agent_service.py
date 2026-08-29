# apps/api/services/agent_service.py

from apps.api.config.settings import settings
from apps.api.providers.memory.registry import get_memory_provider
from apps.api.providers.llm.registry import get_llm_provider

# from apps.api.providers.storage.registry import get_storage_provider
# from apps.api.providers.analytics.registry import get_analytics_provider

from apps.api.core.errors import (
    MemorySearchError,
    MemorySaveError,
    LLMProviderError,
    InvalidMemoryDataError,
    InvalidLLMResponseError,
    ProviderInitError,
)


class AgentService:

    def __init__(self):
        try:
            self.memory = get_memory_provider(settings.memory_provider)
        except Exception as e:
            raise ProviderInitError(f"Failed to initialize memory provider: {e}") from e

        try:
            self.llm = get_llm_provider(settings.llm_provider)
        except Exception as e:
            raise ProviderInitError(f"Failed to initialize LLM provider: {e}") from e

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
            raise MemorySearchError(f"Memory search failed for user '{user_id}': {e}") from e

        # 2. Validate memories is iterable
        if not hasattr(memories, '__len__'):
            raise InvalidMemoryDataError(
                f"Memory search returned non-iterable type: {type(memories).__name__}"
            )

        # 3. Generate LLM response
        try:
            response = await self.llm.generate(
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
            raise MemorySaveError(f"Failed to save conversation for user '{user_id}': {e}") from e

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
        }