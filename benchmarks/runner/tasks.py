# benchmarks/runner/tasks.py

from pathlib import Path

from .schema import BenchmarkTask


def load_task(path: Path) -> BenchmarkTask:
    text = path.read_text()

    # Parse the task ID from "# T001 — ..."
    first_line = text.splitlines()[0]
    task_id = first_line.split(" — ", 1)[0].lstrip("# ").strip()

    # Extract text between ## Prompt and ## Evaluation
    prompt_section = text.split("## Prompt", 1)[1]
    prompt = prompt_section.split("## Evaluation", 1)[0].strip()

    # Extract text between ## Evaluation and ## Metrics
    evaluation_section = text.split("## Evaluation", 1)[1]
    evaluation = evaluation_section.split("## Metrics", 1)[0].strip()

    # Extract metrics as Markdown bullet items
    metrics_section = text.split("## Metrics", 1)[1]
    metrics = [
        line.removeprefix("- ").strip()
        for line in metrics_section.splitlines()
        if line.strip().startswith("- ")
    ]

    return BenchmarkTask(
        task_id=task_id,
        prompt=prompt,
        evaluation=evaluation,
        metrics=metrics,
    )


def load_tasks(directory: Path) -> list[BenchmarkTask]:
    return [load_task(path) for path in sorted(directory.glob("T*.md"))]
