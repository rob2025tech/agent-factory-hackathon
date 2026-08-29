# apps/api/tests/benchmarks/test_tasks.py

from pathlib import Path

from benchmarks.runner.tasks import load_task, load_tasks


def test_load_task(tmp_path: Path):
    task_file = tmp_path / "T001.md"
    task_file.write_text("""# T001 — Basic Instruction Following

## Prompt

Explain what an API is to a beginner.

## Evaluation

The response should:
- be one sentence
- accurately explain the concept of an API
- use language understandable to a beginner

## Metrics

Measure:
- latency
- success/failure
- response length
""")

    task = load_task(task_file)

    assert task.task_id == "T001"
    assert task.prompt == "Explain what an API is to a beginner."

    assert "be one sentence" in task.evaluation
    assert "accurately explain the concept of an API" in task.evaluation

    assert task.metrics == [
        "latency",
        "success/failure",
        "response length",
    ]


def test_load_tasks(tmp_path: Path):
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()

    (tasks_dir / "T001.md").write_text("""# T001 — Task One

## Prompt

First prompt.

## Evaluation

Evaluate the first response.

## Metrics

Measure:
- latency
- response length
""")

    (tasks_dir / "T002.md").write_text("""# T002 — Task Two

## Prompt

Second prompt.

## Evaluation

Evaluate the second response.

## Metrics

Measure:
- latency
- JSON validity
""")

    tasks = load_tasks(tasks_dir)

    assert len(tasks) == 2

    assert tasks[0].task_id == "T001"
    assert tasks[0].prompt == "First prompt."
    assert tasks[0].evaluation == "Evaluate the first response."
    assert tasks[0].metrics == [
        "latency",
        "response length",
    ]

    assert tasks[1].task_id == "T002"
    assert tasks[1].prompt == "Second prompt."
    assert tasks[1].evaluation == "Evaluate the second response."
    assert tasks[1].metrics == [
        "latency",
        "JSON validity",
    ]

def test_load_repository_tasks():
    tasks = load_tasks(Path("benchmarks/tasks"))

    assert [task.task_id for task in tasks] == [
        "T001",
        "T002",
        "T003",
    ]

    for task in tasks:
        assert task.prompt
        assert task.evaluation
        assert task.metrics