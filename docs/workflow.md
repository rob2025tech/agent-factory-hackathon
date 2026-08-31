# Development Workflow

Long-form workflow reference for this repository: how to take a change
from idea to merged code.

Current as of commit `157d847` on `main` (2026-08-31). Workflow rules
here are durable conventions; statements about current practice and
history are snapshots from that commit. When this document and the
code, configuration, or git history disagree, the repository is
authoritative.

---

## 1. Scope and Division of Labor

Durable knowledge lives in tracked files, each with a distinct owner:

| Document | Owns |
| -------- | ---- |
| `/README.md` | First-time setup, running the app, running tests |
| `/AGENTS.md` | Working rules for AI coding agents and humans: verified facts, engineering rules, verification steps |
| `docs/testing.md` | Testing strategy: configuration, placement, determinism, integration policy, CI behavior |
| `docs/architecture/architecture.md` | How the implemented system works |
| `docs/architecture/architecture-decisions.md` | Why decisions were made (ADR log) |
| `docs/architecture/README.md` | Document map and status discipline |
| this document | The end-to-end change loop |

This document references the others rather than repeating them. The
code is the source of truth everywhere.

---

## 2. The Session Loop

```text
setup → branch → change → verify → commit → merge → push → CI
```

Small, low-risk changes (documentation, ADRs) have landed directly on
`main` in recent history; feature work uses feature branches (§7).
Either way, every change passes the same verify step (§5) before it is
committed.

---

## 3. Setup

The root `README.md` is authoritative for setup: creating the Python
3.11 venv (`.venv`), installing `.[dev]`, activation, starting the API
with `uvicorn apps.api.main:app --reload`, and the `/health` check
(§1–§9 of that document). Run all commands from the repository root
(`docs/testing.md` §3 explains why).

---

## 4. Change Rules by Area

### Backend (`apps/api`)

- Architectural boundaries (thin routers, business logic in services,
  no provider calls from routers, no mixing legacy and next-generation
  components in one path, configuration through `config/settings.py`,
  Pydantic-typed API contracts) are `AGENTS.md` engineering rules; they
  apply to every change.
- New providers, tools, and skills implement the existing base classes
  and register in the matching registry (`AGENTS.md`; see also
  `architecture.md` §7).
- New tests go in `apps/api/tests/nextgen/` unless the change touches
  the legacy path; placement detail and mocking patterns are in
  `docs/testing.md` §4–§5.

### Frontend (`apps/web`)

Two hard rules govern all frontend work:

1. **Vanilla HTML/CSS/JS only.** No npm, React, Vite, or any other
   dependency or build tooling. Current state: the entire UI is a
   single `apps/web/index.html` served at `/ui`. Do not introduce a
   build step, a package manifest, or a framework.
2. **The UI consumes the API; it never re-implements it.** The UI calls
   `POST /execute` and renders the returned `trace` (`context`,
   `skill`, `tool`, `llm`) directly from the response. Agent logic —
   routing, tools, provider selection — stays in the backend; the
   browser only displays what the backend reports.

Because the web UI consumes the typed contract directly, changes to
`ExecuteRequest` / `ExecuteResponse` / `ExecutionTrace` must land
together with updated tests and an updated UI (`AGENTS.md`, "Things Not
to Change Casually").

### Documentation

- How the system works changed → update `architecture.md`.
- A decision was made or reversed → record an ADR.
- A document became outdated → give it a status header; do not silently
  edit it. Maintenance rules: `docs/architecture/README.md`.

---

## 5. Verify Before Commit

The standard loop, from the repository root with the venv active:

```bash
python -m pytest            # report the actual results
ruff check .                # no new findings in files you touched
git status                  # only intended changes
```

Actual-counts rule: never assume a fixed test-count baseline; run the
suite and report what it actually says (`docs/testing.md` §10). Name
each skipped test and confirm it is in the documented skip inventory —
a new, undocumented skip should be investigated, not accepted.

For API changes, additionally start the app and exercise `GET /health`
and `POST /execute` with a mock-backed prompt, and confirm the `trace`
shape matches `ExecutionTrace` (`AGENTS.md`, "Verifying Your Work").

---

## 6. Commit Conventions

- Short imperative commit messages: "Add typed execute API contract",
  "Fix mock adapter execute response contract", "Make mem0 an optional
  dependency".
- Review what is staged before committing; the working tree should
  contain only intentional changes.
- Never commit secrets, `.env` files, or credentials.

---

## 7. Branches and Merges

- Do feature work on a feature branch and merge into the long-lived
  branch with a merge commit (`AGENTS.md` git conventions). Existing
  evidence in history: `dedffd8 Merge branch
  'feature/enhanced-observability-skills'`.
- Observed current practice: small documentation and ADR changes land
  directly on `main`. Use judgment: the larger or riskier the change,
  the more it belongs on a branch.
- Never force-push to `main`.

---

## 8. Push and CI

Push to `origin main` after the local verify step passes. CI is the
final gate: on pushes to `main` and on pull requests it runs the test
suite (integration tests excluded) and ruff. Ruff is currently
non-blocking; pytest is not. Details in `docs/testing.md` §8.
