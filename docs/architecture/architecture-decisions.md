# Architecture Decisions

This document records major architectural decisions for the AI Agent Platform Starter project.

The goal is to document **why** a decision was made—not just **what** was implemented.

Update this document whenever a significant architectural decision is made or reversed. Each ADR should explain the problem being solved, the chosen solution, and the trade-offs.

---

## ADR Index

| ADR | Title | Status |
| --- | ----- | ------ |
| ADR-001 | FastAPI is the Primary Backend | Accepted |
| ADR-002 | Backend Owns Provider Logic | Accepted |
| ADR-003 | Frontend Becomes Presentation Layer | Accepted |
| ADR-004 | Registry is the Single Source of Truth | Accepted |
| ADR-005 | REST API Between Frontend and Backend | Accepted |
| ADR-006 | Incremental Migration | Accepted |
| ADR-007 | Monorepo Structure | Proposed |
| ADR-008 | Invalid LLM Responses Fail Hard | Accepted (backfilled) |
| ADR-009 | Deterministic Keyword Skill Routing with Positional Fallback | Accepted (backfilled) |
| ADR-010 | mem0 Remains an Optional Dependency Behind a Lazy Provider Factory | Accepted (backfilled) |
| ADR-011 | The Execution Trace Is Part of the Typed API/UI Contract | Accepted (backfilled) |
| ADR-012 | Keep the Legacy Pipeline Isolated from the Active Next-Generation Path | Accepted (backfilled) |
| ADR-013 | Legacy Pipeline Is Slated for Migrate-Then-Remove | Accepted |
| ADR-014 | Typed Service Errors Surface as HTTP 500 via a Single Exception Handler | Accepted |
| ADR-015 | Storage and Analytics Providers Are Frozen Scaffolding | Accepted |
| ADR-016 | The Empty Placeholders Are Deleted and the Conversation Stubs Are Frozen Scaffolding | Accepted |

ADR-001 … ADR-007 were recorded when made. ADR-008 … ADR-012 were
backfilled on 2026-08-31 from code, tests, and git history; they record
decisions whose rationale previously lived only in code comments and
rules. Backfilled ADRs distinguish documented intent from inference and
state explicitly where the original rationale is unknown. ADR-013 …
ADR-015 were recorded when made on 2026-08-31; they resolve the former
open questions 2–4 in `architecture.md` §13. ADR-016 was recorded when
made on 2026-08-31; it resolves former open question 1. Former open
question 5 is closed by the Stale tag already carried by
`api-contract.md` — no new decision was needed.

---

# ADR-001: FastAPI is the Primary Backend

**Status:** Accepted

**Date:** 2026-08-05

## Context

Two separate repositories currently exist:

- **ai-agent-platform-starter**
  - FastAPI backend
  - Python provider adapters
  - Provider registry
  - Tests
  - Backend execution services

- **genspark-ai-agent-platform-starter**
  - Next.js frontend
  - TypeScript provider adapters
  - UI dashboards
  - Model selector
  - Playground

Both repositories implement similar concepts independently.

## Decision

Use the FastAPI backend as the long-term foundation of the platform.

## Rationale

Advantages include:

- Existing adapter architecture
- Existing provider registry
- Existing automated tests
- Easier provider integration in Python
- Cleaner separation of frontend and backend

## Consequences

Future frontend work will communicate with FastAPI instead of implementing provider logic directly.

---

# ADR-002: Backend Owns Provider Logic

**Status:** Accepted

**Date:** 2026-08-05

## Context

Both repositories currently implement:

- Provider registry
- Provider adapters
- Provider configuration

Maintaining duplicate implementations increases maintenance cost and the risk of inconsistent behavior.

## Decision

All provider communication will occur through FastAPI.

The frontend will never communicate directly with providers.

## Rationale

Benefits include:

- One provider registry
- One pricing table
- One adapter implementation
- One place to fix bugs
- Easier testing
- Easier onboarding of new providers

## Consequences

TypeScript provider adapters will eventually be removed.

---

# ADR-003: Frontend Becomes Presentation Layer

**Status:** Accepted

**Date:** 2026-08-05

## Context

The current Next.js project contains:

- API communication
- Business logic
- Routing logic
- Provider logic
- UI

This mixes responsibilities.

## Decision

The frontend should focus exclusively on:

- User interface
- User interaction
- Displaying data returned by the backend

Business logic should reside in FastAPI.

## Rationale

Benefits include:

- Smaller frontend
- Easier testing
- Less duplicated logic
- Simpler maintenance

## Consequences

The frontend becomes largely a collection of React components and API calls.

---

# ADR-004: Registry is the Single Source of Truth

**Status:** Accepted

**Date:** 2026-08-05

## Context

Information such as:

- available providers
- models
- pricing
- capabilities

should exist in only one place.

## Decision

The FastAPI Provider Registry will become the authoritative source for:

- Providers
- Models
- Pricing
- Capabilities
- Availability

## Rationale

Without a single source of truth:

- pricing drifts
- models become inconsistent
- features differ between frontend and backend

## Consequences

The frontend will retrieve this information through REST endpoints.

---

# ADR-005: REST API Between Frontend and Backend

**Status:** Accepted

**Date:** 2026-08-05

## Context

The frontend needs access to:

- providers
- models
- chat execution
- history
- settings
- costs

## Decision

All communication occurs through REST APIs.

Examples:

- GET /providers
- GET /models
- POST /chat
- GET /history
- GET /costs
- GET /settings

## Rationale

This creates a clean contract between frontend and backend.

The frontend becomes independent of backend implementation details.

## Consequences

Backend APIs become stable interfaces that multiple frontends could consume.

---

# ADR-006: Incremental Migration

**Status:** Accepted

**Date:** 2026-08-05

## Context

Replacing everything at once would introduce unnecessary risk.

## Decision

Migration will occur one feature at a time.

Recommended order:

1. Model Selector
2. Playground
3. Provider Dashboard
4. Request History
5. Cost Dashboard
6. Settings

## Rationale

Benefits include:

- Smaller pull requests
- Easier testing
- Easier rollback
- Faster debugging

## Consequences

Both repositories may temporarily coexist during migration.

---

# ADR-007: Monorepo Structure

**Status:** Proposed

**Date:** 2026-08-05

## Context

The project currently separates backend and frontend into different repositories.

## Proposed Structure

```
ai-agent-platform-starter/

apps/
    api/
    web/

docs/
tests/
```

## Rationale

A monorepo provides:

- shared documentation
- shared CI/CD
- easier dependency management
- unified version history

## Consequences

The frontend repository will eventually be merged into the main project.

---

# ADR-008: Invalid LLM Responses Fail Hard

**Status:** Accepted (backfilled)

**Date:** 2026-08-31 (backfill date; the decision is evidenced in code and tests introduced with the next-generation pipeline)

## Context

`LLMProvider.generate()` can return `None`. The pipeline must decide whether to treat that as a valid empty response or as a failure.

## Decision

An LLM response of `None` raises `InvalidLLMResponseError`. It is never silently converted into an empty response.

## Rationale

Documented in the DECISION comment in `apps/api/services/agent_service.py`: treating `None` as a hard error is a deliberate trade-off. The comment names the alternative — allow `None` and handle it downstream for graceful degradation — and states that reversing the decision requires changing that behavior. No rationale beyond this comment is recorded in the repository.

## Alternatives considered

Graceful degradation (allow `None`, handle it downstream) — explicitly named and rejected in the DECISION comment.

## Consequences

- LLM providers must return a string or raise; `None` is not a valid provider result.
- Tests pin the behavior (`tests/nextgen/test_agent_service_edge_cases.py`).
- Reversing this decision requires updating the service, the downstream handling, and the tests together.

## Evidence

- DECISION comment in `apps/api/services/agent_service.py` (LLM response validation)
- `apps/api/core/errors.py` — `InvalidLLMResponseError`
- `apps/api/tests/nextgen/test_agent_service_edge_cases.py` — asserts the raise
- Commits `76be5e1`, `0bd3cff`

---

# ADR-009: Deterministic Keyword Skill Routing with Positional Fallback

**Status:** Accepted (backfilled)

**Date:** 2026-08-31 (backfill date; routing semantics introduced in commit `0bd3cff`)

## Context

Skill selection must be reproducible and testable; the starter has no infrastructure for learned or LLM-based routing.

## Decision (evidenced directly by code and tests)

- Case-insensitive keyword substring matching scores each skill: one point per keyword contained in the prompt.
- `priority` contributes `0.1×` per priority point, and only among skills that matched at least one keyword. It never causes selection on its own.
- The highest-scoring skill wins.
- A prompt matching nothing falls back to `skills[0]` — registry position, not a lookup for a skill named `default`.
- The selected skill's `backend` drives LLM provider resolution in `AgentService`.

Direct evidence: `apps/api/skills/router.py` docstring, `apps/api/tests/nextgen/test_skill_routing.py` (the fallback test asserts `echo`, the registry's first entry), and `apps/api/services/agent_service.py`.

## Consequences (inferred from the evidenced semantics)

- Registry position is load-bearing: whichever skill is registered first is the fallback.
- Reordering `skills/registry.py` changes behavior even when no skill definition changes.
- The registry may contain a skill named `default`; the name gives it no special routing role.
- Changing these semantics requires updating the router, the tests, and `AGENTS.md` together ("Skill router fallback semantics" is listed under Things Not to Change Casually).

## Alternatives considered

None recorded in the repository. Priority-driven selection and name-based default lookup are contradicted by the router's docstring, but there is no record that they were formally considered.

## Evidence

- `apps/api/skills/router.py`, `apps/api/skills/registry.py`
- `apps/api/tests/nextgen/test_skill_routing.py`
- `apps/api/services/agent_service.py` (backend-driven provider resolution)
- Commit `0bd3cff` "Add skill-based routing, new tools, and richer execution trace schema"

---

# ADR-010: mem0 Remains an Optional Dependency Behind a Lazy Provider Factory

**Status:** Accepted (backfilled)

**Date:** 2026-08-31 (backfill date; decision introduced in commit `572dd7d` "Make mem0 an optional dependency")

## Context

The memory registry includes a provider backed by the external `mem0ai` package. Installing it unconditionally would add a heavy dependency for users who do not use that provider, while the application must run with a default install and no secrets.

## Decision

- `mem0ai` is an optional extra: `pip install '.[mem0]'` (`pyproject.toml`).
- `providers/memory/registry.py` registers provider factories rather than classes; the mem0 factory imports `Mem0Memory` lazily.
- Selecting mem0 without the extra raises an actionable `ImportError` that names the install command.
- The configured default memory provider is `evermind` (`config/settings.py`).

## Rationale

Keeping the default install light and failing with actionable guidance is evident from the implementation and the commit. The repository does not record why `evermind` specifically was chosen as the default; that reason is unknown.

## Alternatives considered

- Making `mem0ai` a hard dependency — rejected in practice by commit `572dd7d`; no written rationale.
- Eager module-level import: the legacy module `apps/api/memory/mem0_memory.py` imports `mem0` at module top level. The active registry avoids that pattern; the repository does not state whether this contrast was a motivating factor.

## Consequences

- The base install and CI never require `mem0ai`.
- Future providers with optional dependencies must follow the same lazy-factory pattern.
- Memory provider selection remains configuration-driven (`settings.memory_provider`).

## Evidence

- Commit `572dd7d` "Make mem0 an optional dependency"
- `apps/api/providers/memory/registry.py`, `apps/api/providers/memory/mem0.py`
- `pyproject.toml` (`[project.optional-dependencies] mem0`)
- `apps/api/config/settings.py`

---

# ADR-011: The Execution Trace Is Part of the Typed API/UI Contract

**Status:** Accepted (backfilled)

**Date:** 2026-08-31 (backfill date; trace introduced in commit `76be5e1`, schema enriched in commit `0bd3cff`)

## Context

`POST /execute` returns how the response was produced, not only the response itself, and the web UI renders that information. What the response includes — and how it may change — therefore needs to be settled.

## Decision — what is implemented

- `AgentService` assembles the trace from the actual values of the execution: context (`user_id`, `task`), selected skill, executed tool name and output, resolved LLM backend, and generated output.
- The router returns it as `ExecuteResponse.trace`, validated by Pydantic into the `ExecutionTrace` model family.
- In the current pipeline the trace is assembled after `llm.generate()` and before `memory.save()`; it therefore reflects a generated-but-not-yet-saved execution. This ordering is described here as observed behavior, not elevated to a separate decision.

## Decision — what the contract requires

- `ExecutionTrace` (with `ContextTrace`, `ToolTrace`, `LLMTrace`) in `apps/api/models/response_models.py` is part of the API response contract and is consumed by `apps/web`.
- Schema changes require corresponding test and UI updates (`AGENTS.md`, Things Not to Change Casually).
- `context` and `llm` are required parts of the trace; the active path must keep populating them.

## Decision — what remains optional/forward-looking

- The richer fields (`trace_id`, `timestamp`, `total_duration_ms`, `skill_selection`, `tools[]`, `memory`, `status`) are declared in the schema but not populated by the active pipeline. They are reserved for future observability work: populating them is additive, while removing or repurposing them is a contract change.
- The `tool` field carries only the first executed tool today; `tools[]` is the designated place for per-tool detail.

## Alternatives considered

None recorded in the repository.

## Consequences

- The trace schema is not an internal implementation detail; it must not drift from the UI's expectations.
- Providers and services must surface real values rather than placeholders, because the trace is contractually visible.

## Evidence

- `apps/api/models/response_models.py`, `apps/api/services/agent_service.py` (trace assembly), `apps/api/routers/execute.py`
- `apps/web/index.html` (trace consumption)
- Commits `76be5e1` "Add observable agent factory execution slice", `0bd3cff` "Add skill-based routing, new tools, and richer execution trace schema"

---

# ADR-012: Keep the Legacy Pipeline Isolated from the Active Next-Generation Path

**Status:** Accepted (backfilled)

**Date:** 2026-08-31 (backfill date; isolation established as the next-generation pipeline became `POST /execute`, commits `516db03`–`0bd3cff`)

## Context

The repository contains two execution pipelines: the next-generation `AgentService`/`providers/` architecture and the older `ExecutionService`/`adapters/` architecture. When the next-generation path became `POST /execute`, the legacy components remained in the repository. The repository does not record why the legacy code was retained.

## Decision

- `POST /execute` runs exclusively on the next-generation pipeline (`AgentService`, `providers/`).
- Legacy components (`services/execution_service.py`, `adapters/`, `apps/api/memory/`) remain in the repository but are currently unwired: no router invokes them.
- Active execution paths should not casually mix legacy and next-generation components.

## Open question

Resolved by ADR-013 (2026-08-31): the legacy pipeline is slated for
migrate-then-remove, with the capabilities to preserve identified
there. Until that migration happens, this ADR's isolation rule remains
in force.

## Consequences

- Changes to legacy components have no effect on `/execute` unless wiring decisions change.
- Work touching legacy files must be explicitly scoped as legacy work.
- `keep-replace-remove.md` lists "Execution Service — Keep"; that statement conflicted with the disposition above and is superseded by ADR-013. The historical document is preserved unedited.

## Evidence

- `apps/api/main.py` (mounted routers), `apps/api/routers/execute.py` (legacy import commented out)
- `AGENTS.md` (Architectural Boundaries; Things Not to Change Casually)
- `docs/architecture/architecture.md` §9 and §13
- Commit history `516db03` onward (next-generation pipeline replacing the adapter path)

---

# ADR-013: Legacy Pipeline Is Slated for Migrate-Then-Remove

**Status:** Accepted

**Date:** 2026-08-31

## Context

ADR-012 recorded the isolation of the legacy pipeline
(`services/execution_service.py`, `adapters/`, `apps/api/memory/`) and
explicitly left its eventual removal or migration as an open question.
The historical `keep-replace-remove.md` lists "Execution Service" under
**Keep**, which conflicts with that treatment.

## Decision

The legacy pipeline is slated for **removal, preceded by migration** of
any capability worth preserving. This ADR records the disposition only:
no migration and no deletion are performed with it, and ADR-012's
isolation rule remains fully in force until the migration happens.

Migration boundary — capabilities to preserve or explicitly drop:

- **Cerebras integration shape** (legacy `CerebrasAdapter` plus
  `tests/integration/test_cerebras_adapter.py`).
- **OpenAI integration shape** (`openai_adapter.py`, unregistered).
- **Snowflake adapter shape** (`snowflake_adapter.py`, unregistered).
- Legacy conversation memory (`apps/api/memory/`) — superseded by
  `providers/memory/`; droppable unless a reason to keep it is stated.

If the platform needs these backends in the future, they must be
implemented as next-generation providers (`providers/llm/` etc.) — not
re-wired through the legacy path.

## Rationale

The legacy path is unwired, duplicates the provider abstractions, has a
known runtime mismatch (`execute_agent` passes an `ExecuteRequest` to
`select()`, which expects a prompt string), and forces the docs to
carry the Keep-vs-frozen contradiction. Indefinite retention costs
documentation accuracy; outright deletion would discard integration
shapes before their value is decided.

## Consequences

- `keep-replace-remove.md`'s "Keep" entry is superseded by this ADR.
  The document stays tagged Historical and is preserved unedited.
- The `AGENTS.md` rule to leave legacy files alone unless explicitly
  scoped remains in force until the migration.
- Tests that depend on legacy code (`tests/test_mock_adapter.py`,
  `tests/integration/test_cerebras_adapter.py`) are migrated or removed
  together with it.
- The actual migration/removal is a separate future task requiring its
  own plan; it must update or supersede this ADR when it lands.

---

# ADR-014: Typed Service Errors Surface as HTTP 500 via a Single Exception Handler

**Status:** Accepted

**Date:** 2026-08-31

## Context

`apps/api/core/errors.py` defines the `AgentServiceError` hierarchy,
but no exception handlers were registered on the app. Uncaught service
errors surfaced as FastAPI's bare HTTP 500 with no typed body, and the
hierarchy had no external manifestation (open question in
`architecture.md` §13).

## Decision

A single `exception_handler(AgentServiceError)` registered in
`apps/api/main.py` returns:

- HTTP status **500** for every `AgentServiceError` subclass;
- a dedicated `ErrorResponse` body (`apps/api/models/error_models.py`)
  with `error_type` (the exception class name) and `detail` (the
  exception message).

The error body is a separate schema; `ExecuteResponse` is unchanged.
Differentiated status codes per error subclass are explicitly deferred.

## Rationale

The minimal mapping that makes service failures typed and observable
without redesigning the success contract. It keeps the typed-contract
principle at the error boundary while avoiding an invented
status-code mapping. Pydantic request-validation errors remain 422.

## Consequences

- Clients can rely on `{error_type, detail}` for `/execute` service
  failures.
- Covered by `apps/api/tests/nextgen/test_error_handler.py`.
- If clients later need differentiation (e.g. 502 for upstream provider
  failures), that is a new decision requiring its own ADR and contract
  update.

---

# ADR-015: Storage and Analytics Providers Are Frozen Scaffolding

**Status:** Accepted

**Date:** 2026-08-31

## Context

`providers/storage/` and `providers/analytics/` contain ABCs and
incomplete classes: `LocalStorage` and `ButterbaseStorage` do not
implement `get()` and cannot be instantiated; `ButterbaseStorage.save`
is a stub; `LocalAnalytics.record` writes invalid JSON;
`SnowflakeAnalytics.record` references an undefined function. There are
no registries, `AgentService` hooks are commented out, and
`settings.storage_provider` / `settings.analytics_provider` consume
nothing. The Snowflake scaffold is tied to the hackathon demo plans in
`docs/hackathon/`. Whether this area was planned or abandoned was an
open question in `architecture.md` §13.

## Decision

Freeze the storage/analytics code exactly as it is and document it as
**scaffolding, not implemented providers**:

- do not wire it into `AgentService`;
- do not implement or "fix" the scaffolds incidentally;
- do not delete it in this decision;
- treat the `storage_provider` / `analytics_provider` settings fields
  as inactive configuration.

Implementation (or removal) becomes a separate task if and when the
capability is actually needed.

## Rationale

Deleting the scaffolds would pre-empt the open hackathon direction
(Snowflake); implementing them without requirements would invent an
API. Freezing with explicit documentation is the honest minimum that
keeps agents and humans from mistaking stubs for working providers.

## Consequences

- Agents must not treat storage/analytics as usable providers or
  reference them as extension points.
- Future implementation must complete the ABCs, add registries, wire
  through settings, add tests, and update or supersede this ADR.

---

# ADR-016: The Empty Placeholders Are Deleted and the Conversation Stubs Are Frozen Scaffolding

**Status:** Accepted

**Date:** 2026-08-31

## Context

`architecture.md` §13 (former open question 1) listed files whose
intended role was not established by the code:

- Eight 0-byte files: `routers/auth.py`, `services/auth_service.py`,
  `services/skill_service.py`, `services/memory_service.py`,
  `services/storage_service.py`, `services/model_router.py`,
  `repositories/base_repository.py`, `providers/nebius/client.py`.
- Two stubs: `services/conversation_service.py` and
  `repositories/conversation_repository.py`.

All ten arrived in the initial `Hackathon baseline` commit and were
never touched since. Nothing imports or wires any of them; the only
references were documentation inventories and the generated
`egg-info/SOURCES.txt`. `conversation_repository.py` duplicates what
the wired `/butterbase` router already does directly;
`conversation_service.py` is a docstring with an unwired layering
sketch plus an empty function. `providers/nebius/` contained only the
empty `client.py` (no `__init__.py`). "Authentication" appears
elsewhere only in historical wish lists, not in any active plan.

## Decision

- Delete the eight 0-byte files outright. `providers/nebius/` is
  removed with its only file.
- Freeze `conversation_service.py` and `conversation_repository.py` in
  place as **scaffolding, not implemented functionality**: do not wire
  them, do not extend them, do not delete them in this decision.
- Leave `settings.nebius_api_key` in place. It remains an orphan key;
  removing a settings field is a configuration-surface change this
  decision does not justify.

If a deleted capability is ever genuinely needed, it is reintroduced
through the standard extension path (define abstraction → implement →
register → wire → test), not by restoring an empty file.

## Rationale

Empty files cannot encode intent; their presence misled agents into
treating them as architecture and forced the documentation to carry
their inventory. Deleting them is lossless — there is no content to
migrate, unlike the ADR-013 legacy shapes. The two conversation stubs
are kept because they contain the only concrete sketch of a
conversation-persistence layer over Butterbase, and whether that layer
is wanted remains an open product question.

## Consequences

- The eight files are removed from the tree; §13 open question 1 is
  resolved.
- Open question 5 is closed separately: `api-contract.md` already
  carries a Stale tag (2026-08-31) pointing to the implemented
  contract; no further change to that document is needed.
- The conversation stubs are documented as frozen, unwired scaffolding
  in `architecture.md` §3 and §10; they are not extension points.
- The tracked `ai_agent_platform_starter.egg-info/` build artifact was
  deliberately left untouched; untracking it is a separate hygiene
  concern.

---

# Future ADRs

Examples of future decisions to document:

- Authentication strategy
- Database selection
- Background job processing
- Streaming architecture
- Logging
- Cost tracking
- Deployment strategy
- CI/CD pipeline
- Plugin architecture