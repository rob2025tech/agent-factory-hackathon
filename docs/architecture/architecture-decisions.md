# Architecture Decisions

This document records major architectural decisions for the AI Agent Platform Starter project.

The goal is to document **why** a decision was made—not just **what** was implemented.

Update this document whenever a significant architectural decision is made or reversed. Each ADR should explain the problem being solved, the chosen solution, and the trade-offs.

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

# Future ADRs

Examples of future decisions to document:

- Authentication strategy
- Database selection
- Background job processing
- Streaming architecture
- Memory architecture (mem0 or alternative)
- Observability
- Logging
- Cost tracking
- Deployment strategy
- CI/CD pipeline
- Plugin architecture