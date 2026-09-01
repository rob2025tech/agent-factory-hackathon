# AGENTS.md

Working instructions for AI coding agents (Qoder, Codex, Claude Code, or
others) modifying this repository.

This document has three tiers:

- **Verified Facts** — repository state confirmed from code and config.
- **Engineering Rules** — durable conventions; follow them on every change.
- **Recommendations** — guidance that usually helps; use judgment.

---

# I. Verified Facts

## Project Purpose

FastAPI starter for building AI agent platforms ("Agent Factory"). It
implements a deterministic, observable agent execution slice: prompt →
memory search → skill selection → tool execution → LLM provider → memory
save, with an execution trace in the API response.

## Repository Structure

```text
apps/
  api/                  # FastAPI application (the backend)
    main.py             # App entrypoint; mounts routers + /ui static files
    routers/            # health, execute, butterbase (thin HTTP layer)
    services/           # Business logic
    skills/             # Skill definitions + keyword router
    tools/              # Deterministic tools
    providers/          # Active provider world: llm/, memory/, storage/, analytics/
    adapters/           # Legacy backend adapters (ADR-013: migrate-then-remove)
    memory/             # Legacy in-memory conversation store
    models/             # Pydantic request/response models (API contract)
    core/               # ExecutionContext, error hierarchy
    config/settings.py  # pydantic-settings; reads apps/api/.env
    tests/              # unit, nextgen/, integration/, benchmarks/, legacy/
  web/                  # Static demo UI served at /ui; consumes the API
benchmarks/             # Standalone benchmark harness + task definitions
docs/architecture/      # ADRs and architecture docs
.github/workflows/      # CI: pytest + ruff
```

## Tool-Specific Instruction Files

`AGENTS.md` is the canonical cross-agent source of truth. Tool-specific
files exist alongside it:

- `.claude/rules/rocketride.md` — Claude-specific, installer-managed
  (RocketRide pointer). Do not hand-edit.
- `.github/copilot-instructions.md` — Copilot-specific, installer-managed
  (RocketRide pointer). Do not hand-edit.
- `.rocketride/` — gitignored third-party RocketRide documentation; the
  canonical reference for RocketRide work.

`CLAUDE.md` does not exist. Create it only if genuinely Claude-specific
behavior appears, and then as a thin import of `AGENTS.md` — never a copy.

`.qoder/rules/` does not exist. Create Qoder rule files only when
`AGENTS.md` grows too large to keep in one file or Qoder-specific topics
appear; split by topic and never duplicate `AGENTS.md` content.

No scoped subdirectory `AGENTS.md` files exist. Add one only when a
subdirectory (e.g., a populated `packages/`) needs its own context.

## Development Environment

- Virtual environment at `.venv/`. First-time setup:
  `python3.11 -m venv .venv && python -m pip install -e ".[dev]"`.
- Optional extra `.[mem0]` installs the optional memory provider
  dependency.
- Configuration lives in `apps/api/.env` (gitignored). All settings in
  `config/settings.py` have defaults so the app runs without secrets.

## Python Requirements

- Python >= 3.11 (see `pyproject.toml` and `.python-version`).
- Tooling configured: black, ruff, mypy (settings in `pyproject.toml`).

## Running the Application

```bash
uvicorn apps.api.main:app --reload     # http://127.0.0.1:8000
curl http://127.0.0.1:8000/health      # expect {"status":"ok"}
```

Routes: `GET /`, `GET /health`, `POST /execute`, `/butterbase/*`, static UI
at `/ui` (path resolved independent of CWD).

## Running Tests

```bash
python -m pytest                        # unit suite; integration deselected by default
python -m pytest -ra                    # include skip reasons
python -m pytest -m integration         # needs external services (e.g. local Ollama)
python -m pytest apps/api/tests/nextgen -q
python -m pytest apps/api/tests/benchmarks -q
```

`pyproject.toml` sets `testpaths = ["apps/api/tests"]` and deselects the
`integration` marker by default. CI runs pytest (excluding
`apps/api/tests/integration/`) and ruff on pushes and pull requests.

## Two Coexisting Execution Pipelines

**Active (next-generation)** — what `POST /execute` uses:

`routers/execute.py` → `services/agent_service.py` (`AgentService`):
`memory.search` → build `ExecutionContext` → `skills.router.select(prompt)`
→ run the skill's tools → resolve LLM from the skill's `backend` →
`llm.generate` → build trace → `memory.save`. Errors raise typed exceptions
from `core/errors.py` (`AgentServiceError` hierarchy). An LLM response of
`None` is intentionally a hard error (decision documented in code).

**Legacy (not wired to any router):**

`services/execution_service.py` + `adapters/` registry (`BaseAdapter`:
mock/ollama always registered; cerebras only when `cerebras_api_key` is
set; openai/snowflake exist but are unregistered) +
`memory/memory_manager.py`. Changes here do not affect `/execute`. The
legacy pipeline is slated for migrate-then-remove (ADR-013); do not
extend it.

## Provider / Registry Architecture

- `providers/llm/`: `LLMProvider` ABC, `async generate(prompt, memories) -> str`;
  registry maps names to classes (mock, ollama, fireworks).
- `providers/memory/`: `MemoryProvider` ABC (`save`, `search`); registry of
  factories; one provider lazy-imports an optional dependency.
- `tools/registry.py`: name → tool instance; `BaseTool.execute(input_text) -> str`.
- `skills/registry.py`: list of Pydantic `Skill` models (`name`, `backend`,
  `tools`, `keywords`, `priority`).
- Legacy `adapters/registry.py`: name → `BaseAdapter` instance.

## Skill Routing Semantics

`skills/router.py` scores keyword matches; `priority` is only a tie-breaker
among skills that matched at least one keyword. A prompt matching nothing
falls back to `skills[0]` — not the "default" skill.

## Execution Context and Tracing

- `core/execution_context.py`: `ExecutionContext` dataclass;
  `with_metadata`/`set_routing` return new instances (effectively immutable).
- `AgentService` builds a `trace` from real execution values; the schema is
  the Pydantic `ExecutionTrace` family in `models/response_models.py`. The
  web UI consumes this schema.

## API Contract

`POST /execute` is typed end-to-end: `ExecuteRequest` → `ExecuteResponse`
(includes `trace`) in `apps/api/models/`. Note:
`docs/architecture/api-contract.md` describes some endpoints that are
planned, not implemented; the code is the source of truth.

## Memory Boundaries

- Active path: `providers/memory/` (async `save`/`search`, keyed by
  `user_id`), selected via `settings.memory_provider`.
- Legacy path: `apps/api/memory/` — used only by the legacy execution
  service, not by `/execute`.

## Testing Layout

- Async tests use `pytest-anyio`.
- `tests/nextgen/` covers the active pipeline; `tests/legacy/` covers the
  old one; `tests/integration/` requires external services;
  `tests/benchmarks/` wraps the `benchmarks/` harness.
- Mock LLM/backends exist specifically so the pipeline is testable without
  live providers.

---

# II. Engineering Rules

## Architectural Boundaries

1. Keep routers thin: business logic lives in services. Never call
   providers from routers.
2. Never put provider or business logic in `apps/web`; it is a static API
   consumer only.
3. Do not mix legacy (`adapters/`, `memory/`, `execution_service.py`) and
   next-generation (`providers/`, `agent_service.py`) components within one
   execution path.
4. Route all configuration through `config/settings.py`; no hard-coded
   URLs, keys, or provider choices in code.
5. Type every API request and response with Pydantic models.

## Things Not to Change Casually

- `ExecuteRequest` / `ExecuteResponse` / `ExecutionTrace` schemas — they
  are the API and UI contract. Change them only together with tests and
  the UI.
- The `memory.search → llm.generate → memory.save` sequence in
  `AgentService` (marked intentional in code comments).
- Skill router fallback semantics (`skills[0]` on no keyword match).
- pytest configuration (`testpaths`, `addopts`, markers) and the CI
  workflow.
- `.env` handling and gitignore rules.
- `.rocketride/` content (third-party tool docs; touch only when doing
  RocketRide work).
- Legacy pipeline files, unless the task is explicitly about them.

## Coding Conventions

1. Write Python 3.11+ code with type hints on public interfaces and
   docstrings on public classes.
2. Match the import style of the file you edit (both relative and absolute
   `apps.api.*` imports exist).
3. Preserve inline comments that record decisions and trade-offs; when you
   make such a decision, document it the same way.
4. Put new tests in `tests/nextgen/` unless touching the legacy path.
5. Mark any test needing external services or API keys with the
   `integration` marker.
6. Add new providers, tools, and skills by implementing the existing base
   classes and registering them in the matching registry; reuse existing
   abstractions before inventing new ones.

## Git Conventions

1. Write commit messages as short imperative sentences ("Add typed execute
   API contract", "Fix mock adapter execute response contract").
2. Do feature work on feature branches; merge into the long-lived branch
   with merge commits (matches existing history).
3. Keep the working tree free of unintended changes.
4. Never commit secrets, `.env` files, or credentials.

---

# III. Recommendations

## Making Changes Safely

1. Make the smallest change that satisfies the task; refactor
   incrementally and preserve existing behavior unless the task changes it.
2. Read the files you touch and their tests before editing.
3. Run the relevant subset of tests while working, then the full suite
   before finishing.
4. Update `docs/architecture/` ADRs when a decision is made or reversed.
5. Before changing behavior that looks odd, check for a "DECISION" comment
   in code or an ADR — it may be intentional.

## Verifying Your Work

Never assume a fixed test-count baseline; run the suite and report the
actual result:

```bash
python -m pytest            # report the actual passed/skipped/deselected counts
python -m pytest -ra        # confirm skips are the documented optional-service ones
ruff check .                # ensure no NEW findings in files you touched
git status                  # confirm only intended changes
```

For API changes, also start the app and exercise `GET /health` and
`POST /execute` with a mock-backed prompt, and confirm the `trace` shape in
the response matches `ExecutionTrace`.
