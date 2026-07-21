# Repository Agent Instructions

These instructions apply to automated and assisted work in this repository.

## Source-of-truth order

Resolve conflicts in this order:

1. `PROJECT_CHARTER.md` — governing safety, intended use, scope, and change control.
2. `FIRST_VERTICAL_SLICE.md` — contract for the active renal-function and renal-dose feature.
3. Existing public interfaces, tests, and implementation behavior on the target branch.
4. `README.md` — setup commands and high-level repository orientation.
5. `BACKLOG.md` — unresolved decisions and deferred work; backlog items are not approved scope.
6. The current task prompt — authoritative only within the boundaries above.

Do not reconstruct requirements from prior chat history, memory, or earlier task summaries. Use the repository and the current task.

## Scope and deliverables

- Complete one explicit deliverable per task.
- Prefer the smallest coherent change that satisfies observable acceptance criteria.
- Treat adjacent refactors, future integrations, additional medications, and new clinical domains as non-goals unless explicitly approved.
- Put unresolved or deferred ideas in `BACKLOG.md`; do not implement them opportunistically.
- Do not broaden the project charter or first vertical slice implicitly.

## Architecture boundaries

- `domain`: passive typed truth and result objects; no calculation, validation, persistence, network, file, or interface behavior.
- `validation`: structural checks and task-sufficiency checks performed before computation.
- `services`: pure deterministic calculations and clinical workflows with typed inputs and outputs; no direct I/O or file reads.
- `rules`: simple, inspectable matching; no opaque DSL, metaprogramming, or hidden state.
- `content`: versioned clinical rule data, separate from application logic.
- `repositories`: the boundary through which services and use cases obtain content.
- `app`: orchestration of mapping, validation, repositories, services, rules, and result construction.
- `mappers` and `interfaces`: external-to-internal conversion and presentation only; no clinical logic.
- `utils`: generic technical helpers only; do not hide clinical policy in utilities.

## Safety and missing-data conventions

- This is a prototype and is not for direct clinical use.
- Use synthetic or properly de-identified data only; never commit PHI.
- Validate before calculating or matching rules.
- Missing numeric values use `None`, never zero, an empty string, or a sentinel number.
- Unknown categorical values use an explicit `UNKNOWN` enum when the domain defines one.
- Preserve supplied units explicitly. Do not silently infer, normalize, or convert ambiguous units.
- Do not silently choose a weight method, sex coefficient, indication, regimen, route, formulation, or medication identity.
- Unsupported or insufficient cases must fail closed and must not produce a dosing recommendation.
- Preserve assumptions, warnings, evidence, provenance, versions, and reproducible calculation inputs where applicable.
- Calculations and rule matching must use unrounded values; rounding belongs at an explicit presentation boundary.

## Bounded repository reading

Start with:

1. this file;
2. the files named by the current task;
3. the directly relevant implementation file; and
4. the directly relevant test file.

Open additional files only to resolve a direct import, interface contract, failing test, or material safety or scope question. Do not scan the entire repository by default. Read `PROJECT_CHARTER.md` or `FIRST_VERTICAL_SLICE.md` when the task changes clinical behavior, scope, content, supported populations, output states, or safety behavior.

## Implementation practice

- Preserve existing public imports and serialized contracts unless the task explicitly changes them.
- Prefer the standard library unless a dependency has a clear, documented purpose.
- Keep functions and models explicit, typed, deterministic, and easy to inspect.
- Avoid speculative abstractions for future features.
- Add or change tests with behavior changes.
- Do not create task-history or checkpoint files unless explicitly requested.

## Verification workflow

1. Run the narrowest relevant test file or test selection first.
2. Fix targeted failures before expanding verification.
3. Run the full test suite when the change is cross-cutting, changes a shared contract, or is being prepared for merge.
4. Run formatting, lint, type, compile, or contract checks that are already configured and relevant.
5. Report commands and results accurately; do not claim CI or local checks that were not run.

## Close procedure

- Summarize the deliverable and files changed.
- Report verification commands and outcomes.
- State any unresolved risk or limitation.
- Record one exact next action in the repository's designated current-state file when one exists; otherwise place it in the pull-request description.
- Do not append completed-task history to stable scope or architecture documents.
