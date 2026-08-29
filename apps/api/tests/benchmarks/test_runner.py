import pytest

from benchmarks.runner.run import run_benchmark
from benchmarks.runner.schema import BenchmarkTask


class FakeProvider:
    async def generate(self, prompt, memories):
        return "Fake response"


@pytest.mark.anyio
async def test_run_benchmark():
    task = BenchmarkTask(
        task_id="T001",
        prompt="Say hello.",
        evaluation="The response should be one sentence.",
        metrics=["latency", "success/failure", "response length"],
    )

    result = await run_benchmark(
        task=task,
        provider=FakeProvider(),
        provider_name="fake",
        model_name="fake-model",
    )

    assert result.task_id == "T001"
    assert result.provider == "fake"
    assert result.model == "fake-model"
    assert result.response == "Fake response"
    assert result.success is True
    assert result.latency_ms >= 0


class FailingProvider:
    async def generate(self, prompt, memories):
        raise RuntimeError("provider failed")


@pytest.mark.anyio
async def test_run_benchmark_records_failure():
    task = BenchmarkTask(
        task_id="T001",
        prompt="Say hello.",
        evaluation="The response should be one sentence.",
        metrics=["latency", "success/failure", "response length"],
    )

    result = await run_benchmark(
        task=task,
        provider=FailingProvider(),
        provider_name="fake",
        model_name="fake-model",
    )

    assert result.success is False
    assert result.response == ""
    assert result.latency_ms >= 0
