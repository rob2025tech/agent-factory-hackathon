from time import perf_counter
from typing import Protocol

from .schema import BenchmarkResult, BenchmarkTask


class LLMProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        memories: list,
    ) -> str: ...


async def run_benchmark(
    *,
    task: BenchmarkTask,
    provider: LLMProvider,
    provider_name: str,
    model_name: str,
) -> BenchmarkResult:
    start = perf_counter()

    try:
        response = await provider.generate(
            prompt=task.prompt,
            memories=[],
        )

        latency_ms = (perf_counter() - start) * 1000

        return BenchmarkResult(
            task_id=task.task_id,
            provider=provider_name,
            model=model_name,
            response=response,
            latency_ms=latency_ms,
            success=True,
        )

    except Exception:
        latency_ms = (perf_counter() - start) * 1000

        return BenchmarkResult(
            task_id=task.task_id,
            provider=provider_name,
            model=model_name,
            response="",
            latency_ms=latency_ms,
            success=False,
        )
