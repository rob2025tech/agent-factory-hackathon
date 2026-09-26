# apps/api/services/agent_service.py

from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

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
from apps.api.skills.registry import skills
from apps.api.skills.router import explain as explain_skill_selection
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
        # Overall execution timing and identity for the observability
        # trace (ADR-011 reserved fields: trace_id, timestamp,
        # total_duration_ms). Monotonic clock for durations; timezone-aware
        # UTC for the timestamp.
        overall_start = perf_counter()
        trace_id = str(uuid4())
        timestamp = datetime.now(UTC)

        # 1. Search memory
        search_start = perf_counter()
        try:
            memories = await self.memory.search(
                user_id=user_id,
                query=prompt,
            )
        except Exception as e:
            raise MemorySearchError(
                f"Memory search failed for user '{user_id}': {e}") from e
        search_duration_ms = (perf_counter() - search_start) * 1000

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

        # Time skill selection and capture the reason implicit in the
        # existing router behavior (no new routing algorithm).
        selection_start = perf_counter()
        skill = select_skill(prompt)
        selection_duration_ms = (perf_counter() - selection_start) * 1000
        selection_reason = explain_skill_selection(prompt)

        context = context.with_metadata(skill=skill.name)

        # Run the skill's registered tools (deterministic).
        # tool_outputs preserves existing first-tool/context behavior;
        # tool_traces records per-tool detail for the tools[] trace field.
        tool_outputs = {}
        tool_traces = []
        for order, tool_name in enumerate(skill.tools):
            tool = tools.get(tool_name)
            if tool is not None:
                tool_start = perf_counter()
                tool_output = tool.execute(prompt)
                tool_duration_ms = (perf_counter() - tool_start) * 1000
                tool_outputs[tool_name] = tool_output
                tool_traces.append(
                    {
                        "name": tool_name,
                        "input": prompt,
                        "output": tool_output,
                        "duration_ms": tool_duration_ms,
                        "order": order,
                    }
                )

        if tool_outputs:
            context = context.with_metadata(tool_outputs=tool_outputs)

        # Resolve the LLM for the selected skill's backend.
        # If the backend matches the configured default provider, reuse the
        # provider constructed at init so injected/patched providers apply.
        if skill.backend == settings.llm_provider:
            llm = self.llm
        else:
            llm = get_llm_provider(skill.backend)

        llm_start = perf_counter()
        try:
            response = await llm.generate(
                prompt=prompt,
                memories=memories,
            )
        except Exception as e:
            raise LLMProviderError(f"LLM generation failed: {e}") from e
        llm_duration_ms = (perf_counter() - llm_start) * 1000

        # Populate llm.model only when the resolved provider already exposes
        # a real string model value (e.g. OllamaLLM.model). Reads existing
        # state; does not change the LLMProvider contract. Anything else
        # (absent attribute, non-string) stays None so the field is never
        # fabricated and never breaks the trace contract. tokens_used is left
        # unset because no reliable source exists in this slice.
        llm_model = getattr(llm, "model", None)
        if not isinstance(llm_model, str):
            llm_model = None

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
            "trace_id": trace_id,
            "timestamp": timestamp,
            "status": "ok",
            "context": {
                "user_id": context.user_id,
                "task": context.task,
            },
            "skill": skill.name,
            "skill_selection": {
                "selected_skill": skill.name,
                "available_skills": [s.name for s in skills],
                "selection_time_ms": selection_duration_ms,
                "selection_reason": selection_reason,
            },
            "tool": (
                {
                    "name": first_tool[0],
                    "output": first_tool[1],
                }
                if first_tool is not None
                else None
            ),
            "tools": tool_traces,
            "llm": {
                "provider": skill.backend,
                "model": llm_model,
                "output": response,
                "duration_ms": llm_duration_ms,
            },
        }

        # 5. Save to memory
        save_start = perf_counter()
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
        save_duration_ms = (perf_counter() - save_start) * 1000

        # MemoryTrace is attached after memory.save() so both durations are
        # real measurements (ADR-011 lists trace.memory as an additive field).
        trace["memory"] = {
            "search_query": prompt,
            "memory_count": len(memories),
            "search_duration_ms": search_duration_ms,
            "save_duration_ms": save_duration_ms,
        }

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

        # Total wall-clock duration of the slice, measured from the overall
        # monotonic start; computed last so it bounds every sub-duration.
        trace["total_duration_ms"] = (perf_counter() - overall_start) * 1000

        return {
            "status": "ok",
            "output": response,
            "memory_count": len(memories),
            "trace": trace,
        }
