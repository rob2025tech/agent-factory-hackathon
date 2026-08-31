# Architecture Documentation Map

Entry point for the documentation in `docs/architecture/`.

Two rules for using this directory:

1. **The code is the source of truth.** When a document and the
   implementation disagree, trust the code and update or re-tag the
   document.
2. **Every document carries a status.** Do not act on a document
   marked Historical or Stale without checking the document it points
   to.

## Documents

| Document | What it is | Status |
| -------- | ---------- | ------ |
| `architecture.md` | Authoritative reference for the implemented system: execution model, registries, boundaries, wiring status | **Current** — dated snapshots, see its header |
| `architecture-decisions.md` | ADR log (ADR-001 … ADR-012) with an index table: consolidation-era decisions plus backfilled next-generation decisions | **Current** |
| `api-contract.md` | Early API design (`/api/chat`, `/api/providers`, …) | **Stale** — describes endpoints that were never implemented; the real contract is in `apps/api/models/` and `architecture.md` §4 |
| `future-architecture.md` | Consolidation-era target architecture | **Historical** — depicts the legacy Execution Service / adapter world |
| `migration-plan.md` | Consolidation phases for merging the two source repositories | **Historical** |
| `keep-replace-remove.md` | Consolidation-era keep/replace/remove inventory | **Historical** — contains an open contradiction about the legacy Execution Service; see `architecture.md` §13 |
| `repository-comparison.md` | Comparison of the two source repositories | **Historical** — background for ADR-001 … ADR-006 |
| `feature-matrix.md` | Consolidation-era feature inventory | **Historical** — not a list of implemented features |

## Related documentation outside this directory

| Document | What it is |
| -------- | ---------- |
| `/AGENTS.md` | Working rules for AI coding agents (and a useful handbook for humans): verified facts, engineering rules, verification steps |
| `/README.md` | Local development setup, run, and test instructions |
| `docs/testing.md` | Long-form testing reference: configuration, placement, determinism, integration policy, CI — **Current**, dated snapshots, see its header |
| `docs/workflow.md` | Planned: development workflow (verify, commit, branch, review) |
| `docs/hackathon/` | Ephemeral hackathon planning docs (provider integration, Snowflake demo, token economy) |
| `docs/mac-setup.md` | Machine setup notes |

## Maintenance rules

1. **How the system works** belongs in `architecture.md`. Update it
   when structure changes; keep its snapshot date accurate.
2. **Why a decision was made or reversed** belongs in an ADR in
   `architecture-decisions.md`. Decisions recorded only as code
   comments should eventually be promoted to ADRs.
3. **Documents stop being current by acquiring a status header**, not
   by silent edits. Historical documents are preserved, tagged, and
   left otherwise untouched.
4. **New planning documents** start with a status header and a scope;
   when their work lands, their outcomes move into `architecture.md`
   or ADRs and the planning doc is tagged Historical.
