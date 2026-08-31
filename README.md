# Agent Factory Hackathon

## Local Development

### 1. Clone or copy the project

Place the project wherever you normally keep your development projects.

The examples below use:

```text
<your-project-directory>/agent-factory-hackathon
```

Replace `<your-project-directory>` with your own directory structure.

### 2. Activate the virtual environment

Every new terminal session should activate the project's virtual environment.

From the repository root:

```bash
cd <your-project-directory>/agent-factory-hackathon
source .venv/bin/activate
```

You should see `(.venv)` at the beginning of your shell prompt.

Verify that the correct environment is active:

```bash
which python
which pytest
python --version
```

Both `python` and `pytest` should resolve to:

```text
<your-project-directory>/agent-factory-hackathon/.venv/bin/
```

### 3. First-time setup

If `.venv` does not exist, create it with Python 3.11:

```bash
python3.11 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

### 4. Run the test suite

Prefer:

```bash
python -m pytest
```

rather than:

```bash
pytest
```

Using `python -m pytest` ensures pytest runs with the currently active Python environment.

There is no fixed test-count baseline; the suite changes over time.
Run it and read the actual results. See `docs/testing.md` §10 for the
actual-counts rule and the latest verified snapshot.

To see details about skipped tests:

```bash
python -m pytest -ra
```

### 5. Run the benchmark tests

```bash
python -m pytest apps/api/tests/benchmarks -q
```

### 6. Run the next-generation tests

```bash
python -m pytest apps/api/tests/nextgen -q
```

### 7. Start the API

In one terminal, with the virtual environment activated:

```bash
cd <your-project-directory>/agent-factory-hackathon
source .venv/bin/activate
uvicorn apps.api.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

### 8. Verify the API

In a **different terminal**, activate the virtual environment if necessary, then run:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### 9. Before committing

Run the test suite:

```bash
python -m pytest
```

If linting/formatting tools are configured for the project, also run:

```bash
ruff check .
black .
```

Then check Git:

```bash
git status
git log --oneline -5
```

The working tree should contain only the changes you intentionally made.

## Optional Provider / Integration Tests

Some integration tests may require external services or API keys.

Tests that depend on unavailable optional services may be skipped automatically.

Use:

```bash
python -m pytest -ra
```

to see which tests were skipped and why.

Do not treat an expected, documented optional-test skip as a test failure.

## Development Workflow

A typical development session looks like:

### Terminal 1 — API

```bash
cd <your-project-directory>/agent-factory-hackathon
source .venv/bin/activate
uvicorn apps.api.main:app --reload
```

### Terminal 2 — Tests / Development

```bash
cd <your-project-directory>/agent-factory-hackathon
source .venv/bin/activate
python -m pytest
```

Then make changes, rerun the relevant tests, and run the full suite before committing.
