# Repository Agent Instructions

These instructions apply to automated and assisted work in this repository.

## Source-of-truth hierarchy

Resolve conflicts in this order:

1. `PROJECT_CHARTER.md` — governing safety and scope.
2. `FIRST_VERTICAL_SLICE.md` — stable feature contract.
3. `ARCHITECTURE.md` — component boundaries.
4. `docs/DOMAIN_CONVENTIONS.md` — modeling rules.
5. `docs/SAFETY_INVARIANTS.md` — concise implementation constraints.
6. `CURRENT.md` — present task and next action.
7. `BACKLOG.md` — deferred or unresolved work.

Existing public interfaces, tests, and implementation behavior describe the current code contract but do not supersede the hierarchy above. The current task prompt defines the requested change only within those boundaries.

Do not reconstruct requirements from prior chat history, memory, checkpoint notes, or earlier task summaries. Use the repository and the current task.

## Ordinary implementation context

Ordinary implementation prompts should direct the agent to read only:

1. `AGENTS.md`;
2. `CURRENT.md`;
3. the directly relevant implementation file; and
4. the directly relevant test file.

Do not preload the full project documentation or scan the repository by default. Open additional files only to resolve a direct import, public interface contract, failing test, or material ambiguity that cannot be resolved from the ordinary context.

Open `PROJECT_CHARTER.md` and the full `FIRST_VERTICAL_SLICE.md` only when making a scope, safety, or clinical-content decision. Do not open them merely to orient routine implementation work.

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

Detailed domain-model conventions are centralized in `docs/DOMAIN_CONVENTIONS.md`; concise safety constraints are centralized in `docs/SAFETY_INVARIANTS.md`.

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
- Record one exact next action in `CURRENT.md` when the task changes current project state; otherwise place it in the pull-request description.
- Do not append completed-task history to stable scope or architecture documents.
