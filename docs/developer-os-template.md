# AI Developer OS Template

A portable, repository-agnostic description of the documentation and
working-method system ("Developer OS") that makes a repository durable
and operable by any AI coding agent or a human. It distills the
practices proven in the repository this template was born in, with all
project-specific content removed.

Companion files:

- `AGENTS.template.md` — fill-in skeleton for the canonical agent
  instruction file.
- `docs/developer-os-checklist.md` — concise bootstrap checklist for
  installing this system into a new repository.

---

## 1. Design Principles

1. **Tool independence.** The system must survive the loss of any
   single AI tool. Nothing essential may live only in one tool's
   memory, rules format, or session state.
2. **Durable knowledge lives in tracked files.** Anything an agent
   needs across sessions belongs in the repository, under version
   control. Agent memory holds at most pointers to repo files, never
   the knowledge itself.
3. **The code is authoritative.** Every document says so, explicitly.
   When a document and the code disagree, the code is right and the
   document is fixed — the document is never trusted forward.
4. **Decisions are recorded; observations are not decisions.** A
   deliberate choice becomes an ADR. Observed behavior is described in
   architecture docs, never promoted to a decision without a decision
   actually having been made.
5. **Facts are separated from snapshots, and snapshots are stamped.**
   Durable conventions and point-in-time statements live side by side
   but are labeled as such, and snapshots carry the commit and date
   they were verified at.
6. **Changes are gated.** Work proceeds through explicit stages —
   inspect, propose, approve, execute approved scope, verify — and
   nothing is committed or pushed without explicit instruction.

---

## 2. The Document Set and Ownership

Each durable document owns exactly one concern; documents reference
each other rather than repeating content.

| Document | Owns |
| -------- | ---- |
| `AGENTS.md` | Working rules for agents and humans: verified facts, engineering rules, recommendations |
| Root `README.md` | First-time setup, running the app, running tests |
| `docs/testing.md` | Testing strategy: configuration, placement, determinism, isolation, CI behavior |
| `docs/workflow.md` | The end-to-end change loop: branch → change → verify → commit → push → CI |
| `docs/architecture/architecture.md` | How the implemented system works |
| `docs/architecture/architecture-decisions.md` | Why decisions were made (ADR log) |
| `docs/architecture/README.md` | The document map and status discipline |

Adapt the set to the repository's size, but preserve the property:
**for any durable fact, exactly one document owns it.**

---

## 3. Document Governance

### 3.1 The document map

One file (conventionally `docs/architecture/README.md`) lists every
durable document with its role and its current status. It is the entry
point an agent reads to learn what exists and what to trust.

### 3.2 Status taxonomy

Every document carries a status:

- **Current** — matches the code as of its stamped snapshot.
- **Stale** — once accurate, now out of date; kept visible, not
  trusted.
- **Historical** — intentionally preserved as a record of a past
  state; describes nothing about the present.
- **Planned** — describes intent, not implementation.

### 3.3 Snapshot headers

Long-form documents open with a header of the form:

```text
Current as of commit `<sha>` on `<branch>` (<date>). Statements about
<durable topics> are durable conventions. Statements about <volatile
topics: counts, current behavior, CI runs> are snapshots from that
commit and will drift. When this document and the code or configuration
disagree, the code and configuration are authoritative.
```

The header does three jobs: it stamps the volatile claims, it names
which claims are durable, and it subordinates the document to the code.

### 3.4 Handling stale and historical documentation: tag, don't rewrite

When a document becomes outdated, give it a status header; do not
silently edit it into shape. Silent edits destroy the record of what
was once true and make drift invisible. Rewriting is only right when
the document's purpose is to describe the present and someone commits
to keeping it current.

---

## 4. Architecture Documentation

### 4.1 Implemented vs selectable vs reachable

Systems accumulate components in different states of aliveness. The
architecture document keeps them apart with an explicit inventory
table:

```text
implemented        code exists
registered         present in a registry / selectable
wired              reachable from the running application
```

Each component is listed against all three states. A component that
exists in code but is not reachable must say so — otherwise agents
will route changes through dead code or assume dead code works.

### 4.2 Known Gaps as open questions

Unresolved questions about the codebase live in a numbered "Known
Gaps" section of the architecture document, each phrased as an open
question with its evidence. When a question is resolved — by a
decision, by a tag, or by an explicit defer — the item is struck
through, annotated with its resolution and ADR pointer, and retained
for traceability. The section is empty only when there is genuinely
nothing open; closing it is a milestone, not an accident.

---

## 5. Architecture Decision Records (ADRs)

### 5.1 Format and location

A single-file log with an index table (ADR number | title | status).
Each record has: **Status** (Accepted / Superseded by), **Date**,
**Context**, **Decision**, **Rationale**, **Consequences** — the date
lives in the record, not the index.

### 5.2 Discipline

- Record decisions when they are made, including reversals. A reversal
  gets a new ADR that supersedes the old one; the old one is not
  edited into the new truth.
- Decisions only. If nobody chose it, it is observed behavior and
  belongs in the architecture doc, not the ADR log.
- ADR numbers are never silently reused. If a proposal is rejected
  before being recorded, its number stays free; a later accepted
  record may take it, but the log notes the reuse if it could confuse.
- Cross-reference both ways: architecture doc sections point at the
  ADR that explains them; ADR consequences name the documents they
  updated.

### 5.3 Backfill discipline

When recording decisions after the fact:

- Mark the record as backfilled.
- Separate what is documented intent (comments, history, messages)
  from what is inferred from behavior; label inferences as inferences.
- If the rationale is genuinely unknown, say so. A stated guess is
  useful; an invented rationale is not.

---

## 6. Testing Documentation

A long-form testing reference documents, at minimum:

1. **What the default run guarantees** — which end-to-end paths are
   exercised without external services, and why that works (the
   deterministic defaults that make it possible).
2. **Configuration ground truth** — every setting that affects
   selection, exclusion, or environment, quoted from the config file.
3. **Placement rules** — where new tests go and why; where tests
   needing external resources must live and how they are marked.
4. **Determinism and mocking policy** — the ordered list of approved
   mocking patterns, from "no mocking, exercise the real system"
   downward, with one concrete example each.
5. **CI behavior** — triggers, environment, exact commands, and which
   checks are blocking vs advisory (stamped as a snapshot).
6. **Known exceptions** — inconsistencies that pre-date the current
   rules, recorded as exceptions so nobody copies them.

### 6.1 The actual-counts rule

> Never assume a fixed test-count baseline. Always run the suite and
> report the actual results.

Supporting practices:

- Test counts appear in documents only as stamped snapshots (commit +
  date), explicitly labeled "a snapshot, not a baseline".
- Every skip/exclusion is named and checked against a documented
  inventory (test | mechanism | reason | exit condition). A new,
  undocumented skip is investigated, not accepted.

---

## 7. Workflow Documentation

The workflow document owns the end-to-end change loop:

```text
setup → branch → change → verify → commit → merge → push → CI
```

It records:

- **Division of labor** — the ownership table from §2.
- **Change rules by area** — what applies to every change in each part
  of the repository (backend, frontend, docs), including the
  documentation triggers: *how the system works changed → update the
  architecture doc; a decision was made or reversed → record an ADR; a
  document became outdated → give it a status header, do not silently
  edit it.*
- **Verify before commit** — the standard loop (run the suite and
  report actual counts; lint the touched files for new findings;
  confirm the working tree holds only intended changes), plus any
  surface-level verification required for API/UI changes.
- **Commit, branch, push conventions** — message style, what lands
  directly vs through branches, and what CI enforces.

---

## 8. Operating Practices

These are the working methods the system encodes. They apply to every
agent and human session.

### 8.1 Evidence-based decisions

Verify every claim against code, config, or history before acting on
it — including claims found in documents and memory. Keep observed
facts separate from assumptions; convert relative dates to absolute
ones when recording them.

### 8.2 Read-only inspection before implementation

Every non-trivial change starts with a read-only phase: read the files
involved, their tests, related decisions, and current repository state.
Findings are reported before any modification is proposed.

### 8.3 Explicit scope boundaries

Before executing, the change is specified as: an approved list of
files/actions, a do-not-modify list, and the verification steps that
will run afterward. Anything outside the approved scope that turns out
to be necessary is reported as a deviation for separate approval,
never silently included.

### 8.4 Verification before commit

The full verify loop runs after every change and its actual results
are reported: suite outcome with real counts, lint findings on touched
files, working-tree review, and — for API/UI work — the running
application exercised against its documented contract.

### 8.5 Staged commit/push workflow

Commit and push are separate, explicitly instructed steps. Nothing is
committed without review of the complete diff; nothing is pushed
without an explicit instruction to push.

### 8.6 Retiring agent memory

When knowledge held in agent memory becomes durable repository
documentation, the memory entry is retired: deleted or replaced with a
pointer to the document. Memory never duplicates what the repo already
carries, and memory claims about repository state are re-verified
before use — a memory is a snapshot of the moment it was written.

---

## 9. Adopting the Template

Install the system in this order (details and verification gates in
`docs/developer-os-checklist.md`):

1. Inspect the repository read-only; collect verified facts.
2. Write `AGENTS.md` from `AGENTS.template.md`.
3. Establish the document map, status taxonomy, and snapshot headers.
4. Start the ADR log; backfill only genuine decisions, with the
   backfill discipline.
5. Write the testing reference with the actual-counts rule.
6. Write the workflow document.
7. Close open questions via decide / freeze / defer, each recorded.
8. Verify the whole set against the code, then land it.

Afterwards the system maintains itself through §3.4, §5.2, and §8:
tag stale documents, record new decisions, retire memory into docs.
