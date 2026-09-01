# Testing

Long-form testing reference for this repository.

Current as of commit `4eed39d` on `main` (2026-08-31). Statements about
configuration semantics, placement rules, and policy are durable
conventions. Statements about test counts, the skip inventory, and CI
behavior are snapshots from that commit and will drift as the suite
evolves. When this document and the code or configuration disagree, the
code and configuration are authoritative.

`AGENTS.md` carries the concise agent-facing rules; this document is
the long-form reference and refers to those rules rather than repeating
them.

---

## 1. What the Suite Guarantees

The default test run exercises the entire active execution pipeline
(`POST /execute` → memory search → skill selection → tool execution →
LLM generation → trace assembly → memory save) without any live
external service. This works because the shipped defaults are
deterministic stand-ins (§5): mock-backed skills and the in-memory
`evermind` memory provider.

On every default run the suite therefore verifies:

- the typed API contract (`ExecuteRequest` / `ExecuteResponse` /
  `ExecutionTrace` in `apps/api/models/`),
- skill routing semantics, including the positional `skills[0]`
  fallback,
- tool execution and tool chaining,
- provider contracts and error paths, including the hard failure on a
  `None` LLM response (ADR-008),
- the shape of the execution trace returned by `/execute` (ADR-011).

Live-provider behavior (a real Ollama server, the real Cerebras API)
is covered only by opt-in integration tests (§7).

---

## 2. Configuration Ground Truth

All pytest configuration lives in `[tool.pytest.ini_options]` in
`pyproject.toml`:

| Setting | Value | Effect |
| ------- | ----- | ------ |
| `testpaths` | `["apps/api/tests"]` | Collection is restricted to this directory. |
| `pythonpath` | `["."]` | `apps.api.*` imports resolve from the repository root. |
| `addopts` | `"-m 'not integration'"` | Tests marked `integration` are deselected on every default run. |
| `markers` | `integration: tests requiring external services or API keys` | The only registered marker. |

Async tests run through the pytest plugin bundled with `anyio` itself;
see §6.

The `dev` extra installs `pytest`, `pytest-anyio`, `ruff`, `black`,
and `mypy`. Black and mypy are configured in `pyproject.toml` but are
not run by any automated check (§8).

---

## 3. Running Tests

Run all commands from the repository root. The benchmark tests load
task files through paths relative to the working directory (e.g.
`Path("benchmarks/tasks")` in `tests/benchmarks/test_tasks.py`), so
running from another directory breaks them.

```bash
python -m pytest                        # unit suite; integration deselected by addopts
python -m pytest -ra                    # same, with skip reasons summarized
python -m pytest -m integration         # opt in to integration tests
python -m pytest apps/api/tests/nextgen -q
python -m pytest apps/api/tests/benchmarks -q
```

First-time environment setup (Python 3.11 venv, editable install with
the dev extra) is documented in the root `README.md`.

---

## 4. Layout and Placement Rules

| Location | Content |
| -------- | ------- |
| `apps/api/tests/` (root) | HTTP-level API contract tests using `TestClient` (`test_execute*.py`, `test_health.py`, `test_mock_adapter.py`) |
| `apps/api/tests/nextgen/` | Active-pipeline tests: `AgentService` behavior, edge cases, orchestration, skill routing, trace shape |
| `apps/api/tests/nextgen/providers/` | Per-provider unit tests (`llm/`, `memory/`) that mock the transport boundary |
| `apps/api/tests/legacy/` | Legacy-pipeline tests; currently one file, unconditionally skipped (§10) |
| `apps/api/tests/integration/` | Tests requiring external services or API keys (§7) |
| `apps/api/tests/benchmarks/` | Tests wrapping the standalone `benchmarks/` harness (runner behavior, task-file loading) |

Placement rules:

- New tests go in `nextgen/` unless the change touches the legacy path.
  This is the `AGENTS.md` placement rule; it exists because the active
  pipeline is what ships.
- Any test needing external services or API keys must carry the
  `integration` marker and live in `integration/` (§7).
- There is no `conftest.py` anywhere in the suite; all fixtures are
  file-local (for example the autouse `offline_memory` fixture in
  `nextgen/test_execute_trace.py`). Recommendation: keep new fixtures
  file-local unless a genuine shared need appears.

---

## 5. Determinism and Mocking Policy

The default run is offline because of how the shipped defaults compose:

- Memory: `settings.memory_provider` defaults to `evermind`, an
  in-memory provider.
- LLM: `AgentService` resolves the provider from the selected skill's
  `backend` (`agent_service.py`). Three of the four shipped skills
  (`echo`, `web_search`, `calculator`) are mock-backed. The fourth
  (`default`) is ollama-backed but has no keywords and is unreachable
  through the keyword router — the no-match fallback is positional
  `skills[0]`, which is the mock-backed `echo` skill (see
  `architecture.md` §7). Every routable prompt therefore resolves to
  `MockLLM`.
- `AgentService.__init__` also constructs a provider from
  `settings.llm_provider` (default `"ollama"`); construction does not
  touch the network, and that instance is only used when a skill's
  backend equals `settings.llm_provider`.

Established mocking patterns, in order of preference:

1. **No mocking.** Exercise the real pipeline against the deterministic
   defaults (`nextgen/test_agent_service.py`). Use this whenever the
   behavior under test does not depend on a specific provider output.
2. **Patch a service attribute with `AsyncMock`.**
   `nextgen/test_execute_trace.py` patches `agent_service.memory` in an
   autouse fixture so the trace test stays hermetic while the LLM path
   still runs through the real registry.
3. **Patch the resolution function.** The edge-case, orchestration, and
   validation tests patch
   `apps.api.services.agent_service.get_llm_provider` to inject
   controlled providers (`None` responses, raising providers). Note the
   reuse rule in `agent_service.py`: when `skill.backend ==
   settings.llm_provider` the service reuses its init-time provider
   instance (so patching `agent_service.llm` applies); otherwise it
   calls `get_llm_provider` fresh (so patching that function applies).
   Choose the patch target to match the branch under test.
4. **Patch the transport boundary for provider unit tests.**
   `nextgen/providers/llm/test_ollama.py` patches
   `apps.api.providers.llm.ollama.httpx.AsyncClient.post` and asserts
   the exact request the provider would send.
5. **Duck-typed fakes.** The benchmark tests pass plain objects with a
   `generate(prompt, memories)` coroutine (`FakeProvider`,
   `FailingProvider` in `benchmarks/test_runner.py`); no base class or
   mock library is required.

Mock providers exist specifically so the pipeline is testable without
live AI services — a design principle of the repository
(`architecture.md` §1), not a coincidence of the current defaults.

---

## 6. Async Tests

Async tests run through the pytest plugin that `anyio` itself bundles
(registered under the plugin name `anyio`). The plugin operates in
strict mode:

- Every async test must be decorated with `@pytest.mark.anyio`.
- An unmarked async test fails with "async def functions are not
  natively supported" (verified 2026-08-31).

Two observed facts about the dependency setup (both verified
2026-08-31):

- The `pytest-anyio` entry in the `dev` extra installs a stub
  distribution (version `0.0.0`) that registers no pytest plugin. The
  plugin that actually runs the async tests comes from `anyio` itself.
- Because `anyio` is a transitive runtime dependency (via `starlette`
  and `httpx`), async tests work even in environments that install only
  the base dependencies — including CI (§8). This is an observed
  consequence of the current dependency graph, not a guaranteed
  property: if a future `anyio` release stops bundling the plugin, CI
  and minimal installs would lose async test support unless a plugin is
  installed explicitly.

---

## 7. Integration Test Policy

Rule: any test that needs an external service or an API key must be
marked `@pytest.mark.integration` and placed in
`apps/api/tests/integration/`.

Effects:

- Default runs deselect these tests through `addopts` — they appear as
  `deselected`, not `skipped`.
- Opt in locally with `python -m pytest -m integration`. The current
  integration test requires a local Ollama instance reachable at the
  configured URL.
- CI additionally ignores the whole directory by path (§8), so
  integration tests never run in CI regardless of markers.

Recorded exception: `integration/test_cerebras_adapter.py` uses an
environment-variable `skipif` (`CEREBRAS_API_KEY`) instead of the
`integration` marker. This is a pre-existing inconsistency, not a
second pattern to copy. Its practical effect: the test is collected on
default local runs and reports `skipped` when the key is absent, and in
CI it is excluded only by the path ignore.

---

## 8. CI Behavior

CI is `.github/workflows/tests.yml`:

- Triggers: pushes to `main` and pull requests targeting `main`.
- Environment: Python 3.11 with pip caching. Installs `pip install -e .`
  (base dependencies only, no dev extra), then `pip install pytest
  ruff`.
- Test step: `pytest -q --ignore=apps/api/tests/integration`. The path
  ignore is redundant with the marker deselection and is the stronger
  guarantee in CI.
- Async tests run in CI through the `anyio`-bundled plugin (§6); no
  async test dependency is installed explicitly.
- Ruff step: `ruff check .` with `continue-on-error: true` — lint
  findings are reported as warnings and do not fail the build. The
  2026-08-31 run reported 48 pre-existing findings.
- Black and mypy are configured in `pyproject.toml` but not run in CI.

Latest verified CI run (2026-08-31, commit `4eed39d`): `39 passed,
2 skipped` — the two unconditional skips (§10); the integration
directory is not collected at all.

---

## 9. API-Level Tests and the `backend` Echo Gotcha

HTTP-level tests use `fastapi.testclient.TestClient` against
`apps.api.main:app` directly (root-level contract tests and
`nextgen/test_execute_trace.py`).

Gotcha: the `backend` field in the `/execute` response echoes what the
client sent; it does not identify which provider actually ran
(`routers/execute.py`).

- If the request omits `backend`, the response reports
  `"agent-service"` — the router substitutes its own default; the
  request model's `"mock"` default never reaches the response.
- If the request supplies `backend`, the response echoes it unchanged.
- In both cases execution always runs through `AgentService`; the
  request's `backend` value never selects the provider.

To assert which provider actually executed, read the trace:
`trace["llm"]["provider"]` (ADR-011). Existing tests demonstrate both
behaviors: `test_execute.py` asserts the echoed value;
`nextgen/test_execute_trace.py` asserts `trace["llm"]["provider"] ==
"mock"`.

---

## 10. Current Snapshot and the Actual-Counts Rule

Snapshot from 2026-08-31, run from the repository root in the project
venv. This is the working tree after commit `4eed39d`, with the four
ADR-014 error-handler tests (`tests/nextgen/test_error_handler.py`)
added:

```text
43 passed, 3 skipped, 1 deselected
```

This is a snapshot, not a baseline. The suite has no fixed expected
count, and any claim of the form "there should be N tests" is wrong by
construction. The rule:

> Never assume a fixed test-count baseline. Always run the suite and
> report the actual results.

Skip/deselect inventory at the snapshot date:

| Test | Mechanism | Reason | Exit condition |
| ---- | --------- | ------ | -------------- |
| `integration/test_cerebras_adapter.py` | `skipif` | `CEREBRAS_API_KEY` missing | Set the key (§7 recorded exception) |
| `legacy/test_agent_service_legacy.py` | unconditional `skip` | "Legacy AgentService replaced by nextgen AgentService" | Tied to the open disposition of the legacy pipeline (ADR-012); none planned |
| `nextgen/test_execute_with_memory.py` | unconditional `skip` | "Awaiting semantic memory implementation" | Semantic memory search lands in the active path |
| `integration/test_ollama.py` | deselected | `integration` marker | Opt in with `-m integration` (never runs in CI) |

When reporting results, name each skip and confirm it is one of the
documented ones — or document the new one here.
