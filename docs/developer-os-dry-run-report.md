# AGENTS.template.md Dry-Run Report

Read-only adaptation exercise: the sections Tool-Specific Instruction
Files, Development Environment, Running the Application, Running
Tests, and Key Architecture Facts of `AGENTS.template.md` were filled
in against this repository, with the repository as source of truth.

Date: 2026-08-31. Constraints honored: `AGENTS.md` not edited,
templates not edited, no new instruction files created, no repository
normalization, no inferred facts — every value below carries its
evidence. Nothing committed.

---

## Proposed filled-in sections

### Tool-Specific Instruction Files

| Path | Owning tool | Management model | Hand-edit policy | Purpose |
| --- | --- | --- | --- | --- |
| `.claude/rules/rocketride.md` | Claude Code | installer-managed (RocketRide) | never hand-edit | RocketRide pointer, scoped via globs |
| `.github/copilot-instructions.md` | GitHub Copilot | installer-managed (RocketRide) | never hand-edit | RocketRide pointer |
| `.rocketride/` | — (not an instruction file) | vendored third-party content, gitignored | touch only for RocketRide work | RocketRide docs/schema reference |

Evidence: both files carry `<!-- ROCKETRIDE:BEGIN -->` markers;
`.rocketride/` contains `docs/`, `schema/`, `services-catalog.json`
and is listed in `.gitignore:22`; AGENTS.md "Tool-Specific Instruction
Files" section.

Files that don't exist, with creation triggers:

- `CLAUDE.md` — absent. Trigger: only if genuinely Claude-specific
  behavior appears; then a thin import of `AGENTS.md`, never a copy.
- `.qoder/rules/` — absent. Trigger: only when `AGENTS.md` grows too
  large or Qoder-specific topics appear; split by topic, never
  duplicate.
- Scoped subdirectory `AGENTS.md` — none exist (`find` returns only
  `./AGENTS.md`). Trigger: only when a populated subdirectory needs
  its own context.

### Development Environment

- **Runtime:** Python >= 3.11 — `pyproject.toml:5`
  (`requires-python = ">=3.11"`); `.python-version` pins `3.11.8`.
- **Tooling:** black, ruff, mypy configured in `pyproject.toml`
  (`[tool.black]`, `[tool.ruff]`, `[tool.mypy]`); installed via
  `.[dev]` (`pyproject.toml:17-23`). Note: only pytest and ruff run
  in CI; black/mypy are configured but enforced nowhere.
- **Venv:** `.venv/` at repo root; create with
  `python3.11 -m venv .venv` (`README.md:49`).
- **First-time setup:**
  `python3.11 -m venv .venv && python -m pip install -e ".[dev]"`
  (`README.md:49,61`). Optional extra `.[mem0]` (`pyproject.toml:24-26`).
- **Configuration:** `apps/api/.env`, loaded via
  `SettingsConfigDict(env_file=BASE_DIR / ".env")`
  (`apps/api/config/settings.py:11-14`).
- **Runs without secrets:** yes — every `Settings` field has a
  default; API keys are `str | None = None` (`settings.py:16-33`).
  `.env` is gitignored with a tracked `apps/api/.env.example`
  (`apps/api/.gitignore:9-11`).

### Running the Application

```bash
uvicorn apps.api.main:app --reload     # http://127.0.0.1:8000
curl http://127.0.0.1:8000/health      # expect {"status":"ok"}
```

Evidence: `README.md:109,123`.

Implemented routes (all wired in `apps/api/main.py`):

- `GET /` (`main.py:45-47`), `GET /health` (`routers/health.py`,
  mounted `main.py:50`), `POST /execute` (`routers/execute.py`,
  `main.py:51`), `/butterbase/*` (`routers/butterbase.py`,
  `main.py:52`), static UI at `/ui` with a CWD-independent path
  (`main.py:40-42,54`).
- Configuration-dependent: `/butterbase/*` requires real
  `butterbase_api_base`/`butterbase_api_key`, which default to `None`
  (`settings.py:23-24`).
- Error contract: every `AgentServiceError` surfaces as HTTP 500 with
  `ErrorResponse{error_type, detail}` (`main.py:31-37`, ADR-014).

### Running Tests

```bash
python -m pytest                        # unit suite; integration deselected by addopts
python -m pytest -ra                    # same, skip reasons summarized
python -m pytest -m integration         # opt in; needs external services
python -m pytest apps/api/tests/nextgen -q
python -m pytest apps/api/tests/benchmarks -q
```

- **Test locations** (filesystem): root-level HTTP contract tests
  (`test_execute*.py`, `test_health.py`, `test_mock_adapter.py`);
  `nextgen/` active pipeline; `nextgen/providers/` provider unit
  tests; `integration/`; `legacy/`; `benchmarks/`.
- **Selection config:** `testpaths = ["apps/api/tests"]`,
  `pythonpath = ["."]`, `addopts = "-m 'not integration'"`, one
  `integration` marker (`pyproject.toml:36-42`). Run from the repo
  root (benchmark tests use CWD-relative paths — `docs/testing.md` §3).
- **CI** (`.github/workflows/tests.yml`): pushes/PRs to `main`;
  Python 3.11 with pip cache; `pip install -e .` then
  `pip install pytest ruff`;
  `pytest -q --ignore=apps/api/tests/integration`; ruff step is
  non-blocking (`continue-on-error: true`).
- Long-form policy: `docs/testing.md` (placement rules, determinism,
  mocking policy, skip inventory) — do not repeat it here.

### Key Architecture Facts

- **Active path (what `POST /execute` uses):** `routers/execute.py` →
  `services/agent_service.py` `AgentService`: `memory.search`
  (`agent_service.py:51`) → `ExecutionContext` (`:74`) →
  `skills/router.py` select → skill tools → LLM from the skill's
  `backend` → `llm.generate` (`:102`) → trace → `memory.save`
  (`:142`). Errors raise from the `AgentServiceError` hierarchy
  (`core/errors.py`); a `None` LLM response is a hard error (ADR-008).
- **Two pipelines coexist — the central trap:** legacy
  (`services/execution_service.py` + `adapters/` + `memory/`) is
  registered but not wired to any router; do not mix it with the
  active path (ADR-013: migrate-then-remove).
- **Extension model:** implement the base class, register in the
  matching registry — LLM: `LLMProvider` ABC, registry
  `{mock, ollama, fireworks}` (`providers/llm/registry.py`); Memory:
  factory registry `{evermind, mem0 lazy}`
  (`providers/memory/registry.py`); Tools:
  `BaseTool.execute(input_text) -> str`, name→instance
  (`tools/registry.py`); Skills: Pydantic `Skill` models with
  `name/backend/tools/keywords/priority` (`skills/registry.py`).
- **Routing semantics:** keyword count scores; `priority` is only a
  tie-breaker among keyword-matched skills; no match falls back to
  positional `skills[0]` (`skills/router.py`, verified in code).
- **API contract:** `ExecuteRequest` / `ExecuteResponse` (with
  `trace`) / `ExecutionTrace` in `apps/api/models/`; consumed by the
  `/ui` frontend — change only together with tests and UI.
- **Frozen/scaffolded:** storage/analytics providers (ADR-015) and
  `conversation_service.py`/`conversation_repository.py` (ADR-016)
  exist but are unwired.

---

## Template wording that proved ambiguous

1. **Management model is one-dimensional.** The per-file slot
   `{{which tool}}, {{managed by whom}}, {{purpose}}` conflates three
   distinct axes the dry run needed: owning tool, management model
   (repo-authored vs installer-managed), and hand-edit policy.
   Installer-managed implies do-not-hand-edit, but repo-authored
   files can also carry edit restrictions (`.rocketride/`).
2. **"Instruction file" vs vendored content.** The inventory assumes
   every entry is an instruction file; `.rocketride/` is vendored
   reference docs, not instructions — no row type for it.
3. **Key Architecture Facts shape.** The template offers an unordered
   bullet list of "typical topics"; the real AGENTS.md uses titled
   subsections. No guidance on when to switch.
4. **Smoke check asks for a command, not an expected output** — the
   expectation (`{"status":"ok"}`) is the useful half.
5. **Single start command assumed** — fine here, awkward for repos
   with multiple entry points.

## Repository facts the template cannot represent cleanly

1. **Configured-but-unenforced tooling** (black/mypy installed and
   configured, run nowhere) — an agent could mistake configuration
   for enforcement.
2. **Dead code inside the entry point** (commented-out routes in
   `main.py:11-25`) — only visible on read; no state slot for it.
3. **Cross-cutting optional-dependency story** (`mem0`: env extra +
   lazy factory + isolation test) spans Environment, Tests, and
   Architecture sections; the template forces one home.
4. **The two-pipeline trap** is only a parenthetical note under
   Repository Structure, though it's the single most important
   active-path fact.

## Recommended template improvements (not implemented)

1. Split the tool-specific-file slot into explicit fields: path |
   owning tool | management model | hand-edit policy | purpose — and
   add a row type for vendored third-party content.
2. Promote "coexisting execution paths / generations" from a
   Repository Structure note to a named Key Architecture Facts topic.
3. Add a Development Environment slot for "tooling configured but not
   enforced by any automated check."
4. Recommend titled subsections in Key Architecture Facts when there
   are more than ~3 topics.
5. Have the smoke check capture the expected response, not just the
   command.
6. Note that optional-dependency facts may need cross-references
   rather than a single home.
