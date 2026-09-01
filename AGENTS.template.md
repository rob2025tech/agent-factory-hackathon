# AGENTS.md Template

Portable skeleton for a repository's `AGENTS.md` — the canonical,
agent-neutral instruction file that any AI coding agent (or a human)
reads before modifying the repository.

Copy this file into a new repository as `AGENTS.md` and fill every
`{{placeholder}}`. Keep the three-tier structure; it is the core design.

---

## Authoring Rules

These rules govern the template itself and every future edit to the
resulting `AGENTS.md`. They are the most important part of this file.

1. **Three tiers, never merged.**
   - **Verified Facts** — repository state confirmed from code, config,
     or history. Never write a fact you have not verified; never infer
     a fact from documentation alone. Time-sensitive facts (counts,
     versions, current behavior) carry the date or commit they were
     verified at.
   - **Engineering Rules** — durable conventions that apply to every
     change. Written in the imperative ("Keep routers thin", "Never
     commit secrets"). A rule either holds always or it is not a rule.
   - **Recommendations** — guidance that usually helps. Written with
     visible judgment language ("prefer", "usually", "when possible").
2. **Verify before writing.** Read the code, config, or history a claim
   refers to before stating it as a fact. If it cannot be verified,
   either drop it or move it to Recommendations.
3. **Agent-neutral language.** No tool-specific pronouns or features.
   Tool-specific material lives in thin pointer files (see "Tool-Specific
   Instruction Files"), never copied into this document.
4. **Volatile facts are stamped.** Anything that drifts (test counts,
   dependency versions, "current" behavior) is either omitted or
   stamped with where and when it was verified. Prefer linking to the
   document that owns the detail over repeating it.
5. **Small enough to read in one sitting.** Split into topic files
   before the document becomes unmanageable; never duplicate content
   between files.
6. **When the document and the code disagree, the code is right.** Fix
   the document; do not trust it forward.

---

# I. Verified Facts

## Project Purpose

{{One or two sentences: what this repository is and what problem it
solves. Written from what the code actually does, not from ambition.}}

## Repository Structure

```text
{{Top-level directory tree. For each entry, annotate its purpose.}}
{{Mark states that are not obvious from the code:}}
{{  legacy/       — superseded, still present, not wired}}
{{  frozen/       — deliberately kept, not maintained}}
{{  scaffolded/   — placeholder, not implemented}}
```

Notes on states readers must not confuse:

- {{If the repository has more than one execution path / code generation
  / module era, name them here and say which one is active. State
  explicitly what is NOT wired to anything.}}
- {{If components can exist in distinct states (e.g. implemented vs
  registered vs reachable), name the states and where each component
  stands. A thing that exists in code is not necessarily reachable.}}

## Tool-Specific Instruction Files

`AGENTS.md` is the canonical cross-agent source of truth. Tool-specific
files, when they exist, are thin pointers or extensions — never copies.

{{Inventory each tool-specific instruction file that exists:}}
- {{path}} — {{which tool}}, {{managed by whom}}, {{purpose}}.
  {{Mark files that are installer-managed: "Do not hand-edit."}}

{{For each common tool that has NO file yet, state the creation
trigger so nobody creates one prematurely:}}
- `CLAUDE.md` does not exist. Create it only if genuinely Claude-specific
  behavior appears, and then as a thin import of `AGENTS.md` — never a copy.
- {{Repeat for other tools' convention files, or delete rows that do not
  apply.}}

{{Scoped subdirectory instruction files: state which exist (none?) and
the trigger for adding one — e.g. only when a populated subdirectory
needs its own context.}}

## Development Environment

- {{Runtime(s) and minimum versions, and where that is declared.}}
- {{Virtual environment / workspace location and first-time setup
  commands.}}
- {{Where configuration lives; state explicitly whether the app runs
  without secrets and why.}}

## Running the Application

```bash
{{start command}}     # {{URL / entrypoint}}
{{smoke-check command}}  # {{expected output}}
```

Routes/endpoints: {{concise list; note any whose behavior depends on
configuration or optional dependencies.}}

## Running Tests

```bash
{{full suite command}}   # {{what is included/excluded by default}}
{{subsuite commands}}    # {{what each covers}}
```

{{Where each kind of test lives, briefly (test layout); placement
detail belongs in the testing document.}}

{{How test selection is configured (paths, markers, default exclusions)
and what CI runs. Point to the long-form testing document if one
exists; do not repeat it.}}

## Key Architecture Facts

{{A short set of verified facts an agent needs before touching the
active path. Typical topics:}}
- {{The primary request flow, end to end, through real file names.}}
- {{The extension model: how new {{providers/tools/handlers/plugins}}
  are added (base classes, registries, configuration).}}
- {{Selection/routing semantics that are easy to get wrong.}}
- {{Core data structures shared across layers (the API contract).}}
- {{Error-handling model, especially which failures are intentional.}}
- {{Boundaries between subsystems (e.g. active vs legacy memory).}}
- {{Anything that looks like a bug but is a documented decision —
  point at the comment or ADR.}}

---

# II. Engineering Rules

## Architectural Boundaries

{{Numbered, imperative. Derive each from a real failure mode of this
codebase. Typical shapes:}}
1. {{Layering rule: where each kind of logic lives and where it must
   not appear.}}
2. {{Isolation rule: never mix {{era A}} and {{era B}} components within
   one execution path.}}
3. {{Configuration rule: all configuration through one place; no
   hard-coded URLs, keys, or mode choices in code.}}
4. {{Typing/contract rule: every external boundary is explicitly typed.}}

## Things Not to Change Casually

{{Named structures whose change has outsized blast radius, and the
condition under which they may change. Typical entries:}}
- {{The public API/request/response schemas — change only together with
  their consumers and tests.}}
- {{Sequences or invariants marked intentional in code comments.}}
- {{Build/test/CI configuration.}}
- {{Secret handling and ignore rules.}}
- {{Third-party vendored content — touch only when working on that
  integration.}}
- {{Legacy/frozen files, unless the task is explicitly about them.}}

## Coding Conventions

1. {{Language version and typing expectations.}}
2. {{Match the style of the file being edited (state known divergences
   explicitly rather than silently picking one).}}
3. Preserve inline comments that record decisions and trade-offs; when
   you make such a decision, document it the same way.
4. {{Where new tests go.}}
5. {{How tests requiring external resources are marked/isolated.}}
6. Add new {{components}} by implementing the existing base classes and
   registering them in the matching registry; reuse existing
   abstractions before inventing new ones.

## Git Conventions

1. {{Commit message style, with examples from real history.}}
2. {{Branching model: what lands directly on the long-lived branch,
   what goes through feature branches, how merges happen.}}
3. Keep the working tree free of unintended changes.
4. Never commit secrets, environment files, or credentials.

---

# III. Recommendations

## Making Changes Safely

1. Make the smallest change that satisfies the task; refactor
   incrementally and preserve existing behavior unless the task
   changes it.
2. Read the files you touch and their tests before editing.
3. Run the relevant subset of tests while working, then the full suite
   before finishing.
4. Update architecture documentation and ADRs when a decision is made
   or reversed.
5. Before changing behavior that looks odd, check for a decision
   comment in code or an ADR — it may be intentional.

## Verifying Your Work

Never assume a fixed test-count baseline; run the suite and report the
actual result:

```bash
{{test command}}     # report the actual passed/skipped/excluded counts
{{skip-summary command}}  # confirm skips are the documented ones
{{lint command}}     # ensure no NEW findings in files you touched
git status           # confirm only intended changes
```

{{If the change touches a public surface: also start the application
and exercise the affected endpoint/flow, and confirm the observable
output matches the documented contract.}}

---

## Post-Authoring Checklist

Before considering the document done:

- [ ] Every statement in Section I was verified against code, config,
      or history during this authoring session.
- [ ] No tier bleeds into another (no hedged language in Rules; no
      unverified claims in Facts).
- [ ] No tool-specific content outside the Tool-Specific Instruction
      Files inventory.
- [ ] No content duplicated from other documents — linked instead.
- [ ] Documented statuses (legacy/frozen/scaffolded) match what a
      reader would observe in the code.
