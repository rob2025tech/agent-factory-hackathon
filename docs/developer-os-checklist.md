# Developer OS Bootstrap Checklist

Concise checklist for installing the AI Developer OS (see
`docs/developer-os-template.md`) into a new repository. Work top to
bottom; each phase ends with a gate before the next begins.

## Phase 0 — Inspect (read-only)

- [ ] Read the code, config, build/test setup, and recent history.
- [ ] Verify every fact you plan to rely on against the code — do not
      trust existing documentation or memory unverified.
- [ ] List what is implemented vs registered vs reachable; note dead,
      legacy, frozen, and scaffolded code.
- [ ] Collect open questions; do not resolve anything yet.
- **Gate:** you can state, with evidence, what the repository is, how
  the active path works, and what is unknown.

## Phase 1 — `AGENTS.md`

- [ ] Copy `AGENTS.template.md` to `AGENTS.md`; fill every placeholder
      from Phase 0 evidence.
- [ ] Three tiers kept pure: verified facts stamped, rules imperative,
      recommendations hedged.
- [ ] "Things Not to Change Casually" lists real blast-radius
      structures with their change conditions.
- [ ] Tool-specific instruction files inventoried; creation triggers
      stated for the ones that do not exist yet.
- **Gate:** an agent reading only this file can set up, run, test, and
  change the repository without making a category error.

## Phase 2 — Document governance

- [ ] Document map exists: every durable document, its role, its
      status.
- [ ] Status taxonomy applied: every document is Current / Stale /
      Historical / Planned.
- [ ] Long-form documents carry snapshot headers (commit + date,
      durable-vs-snapshot statement, code-authoritative rule).
- [ ] Outdated documents are tagged, not silently rewritten.
- **Gate:** no document exists whose trustworthiness is unstated.

## Phase 3 — ADR log

- [ ] Single-file log with index table created.
- [ ] Records use Status / Date / Context / Decision / Rationale /
      Consequences.
- [ ] Backfill limited to genuine decisions; backfilled records marked,
      inferences labeled, unknown rationales admitted.
- [ ] Observed behavior NOT recorded as decisions.
- [ ] Architecture doc cross-references ADRs both ways.
- **Gate:** every "why" question about the code has an answer or an
  admitted unknown.

## Phase 4 — Testing reference

- [ ] Documents what the default run guarantees and why (the
      deterministic defaults).
- [ ] Configuration ground truth quoted from the config file.
- [ ] Placement rules, external-resource isolation marker, mocking
      policy (ordered patterns with examples).
- [ ] CI behavior stamped as snapshot; blocking vs advisory checks
      distinguished.
- [ ] Actual-counts rule stated verbatim; counts appear only as
      stamped snapshots; skip/exclusion inventory with exit conditions.
- **Gate:** running the suite from the reference reproduces and
  explains every result, skip, and exclusion.

## Phase 5 — Workflow document

- [ ] Session loop written: setup → branch → change → verify → commit →
      merge → push → CI.
- [ ] Ownership table; change rules per area; documentation triggers
      (system changed → architecture doc; decision made/reversed →
      ADR; doc outdated → status header).
- [ ] Verify-before-commit loop (suite with actual counts, lint touched
      files, working-tree review, surface checks for API/UI).
- [ ] Commit/branch/push conventions and CI gates.
- **Gate:** the loop in the document matches what actually happens in
  history; divergences are either fixed or recorded.

## Phase 6 — Close open questions

- [ ] Each Phase 0 open question gets exactly one disposition:
      **decide** (ADR), **freeze** (tag + record), or **defer**
      (documented with an exit condition).
- [ ] Resolutions recorded in the architecture doc's Known Gaps
      section: struck through, annotated, retained for traceability.
- **Gate:** the open-question backlog is empty or every remaining item
  is an explicit, documented defer.

## Phase 7 — Verify and land

- [ ] Every claim in every new document re-checked against the code.
- [ ] Full test suite run; actual results reported.
- [ ] Complete diff reviewed; working tree holds only intended
      changes.
- [ ] Committed and pushed only on explicit instruction.
- **Gate:** the document set is Current as of the commit that lands it.

## Maintenance loop (every change afterwards)

- [ ] Behavior changed → architecture doc updated (snapshot bumped).
- [ ] Decision made or reversed → new ADR (supersede, never edit).
- [ ] Document outdated → status header, never silent edit.
- [ ] New skip/exclusion → added to the inventory or investigated.
- [ ] Knowledge became durable in the repo → agent memory entry
      retired to a pointer.
- [ ] Verify loop run and actual results reported before commit.
