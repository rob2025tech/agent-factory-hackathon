# benchmarks/runner/schema.py

from dataclasses import dataclass


@dataclass
class BenchmarkTask:
    task_id: str
    prompt: str
    evaluation: str
    metrics: list[str]


@dataclass
class BenchmarkResult:
    task_id: str
    provider: str
    model: str
    response: str
    latency_ms: float
    success: bool
