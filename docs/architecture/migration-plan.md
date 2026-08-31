# Migration Plan

> **Status: Historical (tagged 2026-08-31).** Consolidation plan for
> merging the two source repositories. Phases 1–4 produced outcomes
> still present here (including `apps/web`); later phases reference a
> repository that is no longer part of this project.

## Phase 1

- Compare repositories
- Inventory features
- Identify duplicate implementations

---

## Phase 2

Design backend APIs.

---

## Phase 3

Implement missing FastAPI endpoints.

---

## Phase 4

Create apps/web.

---

## Phase 5

Move one UI page at a time.

Recommended order:

1. Model Selector
2. Playground
3. Provider Dashboard
4. History
5. Cost Dashboard
6. Settings

---

## Phase 6

Delete duplicate TypeScript provider logic.

---

## Phase 7

Update documentation.