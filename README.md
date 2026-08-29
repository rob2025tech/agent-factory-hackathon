Start your API:
This project uses relative imports, so to start uvicorn:

1. Make sure you are in the root directory (i.e. ai-agent-platform-starter)

cd /path/to/ai-agent-platform-starter

2. From the root ai-agent-platform-starter directory, run:

git status
git pull   ### Daily startup
git log --oneline -5

rm -rf .venv   ### Migration / Broken env recovery
python3.11 -m venv .venv   ### Migration / Broken env recovery
source .venv/bin/activate   ### Daily startup

pip install -e ".[dev]"  ### First-time setup / Migration / Broken env recovery

which python
python --version   ### Daily startup

ollama list
ollama pull qwen3:8b

curl http://localhost:11434/api/tags

Recreate apps/api/.env
source .venv/bin/activate

pytest -v   ### Daily startup
black .
ruff check .
ruff check . --fix
ruff check .

uvicorn apps.api.main:app --reload

3. From a different terminal, verify the API with this curl command:

curl http://localhost:8000/health

You should see:

{"status":"ok"}% 

4. If that status said "ok", test the execute endpoint:

curl -X POST http://localhost:8000/execute \
-H "Content-Type: application/json" \
-d '{
  "backend":"mock",
  "prompt":"Hello"
}'

You should see this:

{"status":"ok","backend":"mock","prompt":"Hello","output":"hello from mock backend"}%   

4b.

curl -X POST http://localhost:8000/execute \
-H "Content-Type: application/json" \
-d '{
  "backend":"ollama",
  "prompt":"Say hello in one word."
}'

You should see this:

{"status":"ok","backend":"ollama","prompt":"Say hello in one word.","output":"hello\n"}%   

4c.

curl -X POST http://localhost:8000/execute \
-H "Content-Type: application/json" \
-d '{
  "backend":"cerebras",
  "prompt":"Explain AI agents in one sentence."
}'

You should see this:
{
  "status":"ok",
  "backend":"cerebras",
  "output":"An AI agent is an autonomous software entity..."
}

5. To run both test in one command, you can run:

pytest

6. Before every commit, run:

ruff check .
black .
pytest


## Running Tests

Run the full test suite:

```bash
pytest
```

Recommended during development (shows skipped tests and why):

```bash
pytest -ra
```

Example:

```
4 passed, 1 skipped

SKIPPED [1] apps/api/tests/integration/test_cerebras_adapter.py:
CEREBRAS_API_KEY missing
```

## Optional Provider Tests

Some integration tests require provider API keys.

Without the corresponding environment variable, those tests are skipped automatically.

Example:

- CEREBRAS_API_KEY → enables Cerebras integration tests
- OPENAI_API_KEY → enables OpenAI integration tests (future)
- ANTHROPIC_API_KEY → enables Anthropic integration tests (future)

Use:

```bash
pytest -ra
```

to see which optional tests were skipped and why.


7/29/2026 git commit -m "checkpoint before Genspark changes"