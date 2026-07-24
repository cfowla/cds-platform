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

## Execution-context decision

Determine the execution context once, at the start of the task:

1. Run `git rev-parse --show-toplevel` from the current working directory.
2. If it succeeds and identifies this repository, use that checkout.
3. If it fails, do not search the filesystem for another checkout.
4. Do not run `git clone`, `gh repo clone`, `curl`, or `wget`.
5. When only the GitHub connector is available, create the bounded verification checkout described below.

Do not run broad searches such as:

- `find /`
- `find /home`
- `find /mnt`
- recursive repository discovery outside the current working directory

## Bounded verification checkout

When no complete checkout is available, materialize a bounded checkout at:

`/tmp/cds-platform`

Preserve all repository-relative paths.

Initially materialize only:

1. Files explicitly listed under `Read first`.
2. Focused test files explicitly named by the task.
3. Ancestor `__init__.py` files required to create valid Python packages.
4. `pyproject.toml` only when required for pytest configuration, package metadata, or declared test dependencies.

Do not mirror entire directories or reconstruct the full repository.

## Import-driven expansion

Expand the bounded checkout only when required by focused test collection or execution.

An additional repository file may be fetched only when one of these is true:

1. A focused test directly imports it.
2. A named implementation file directly imports it and test collection reaches that import.
3. Pytest reports a concrete missing in-repository module, fixture, or resource.
4. A focused failure identifies a directly relevant repository convention necessary to complete the task.

For each additional file, record:

- its repository-relative path;
- the importing file or failing test; and
- the exact import, fixture, resource reference, or error requiring it.

Do not fetch a file because it is adjacent, similarly named, generally relevant, or potentially useful.

Follow the import chain lazily, one concrete missing dependency at a time. Do not statically traverse every possible transitive import before running the focused tests.

## Expansion limits

Do not perform more than two dependency-expansion rounds without a concrete new error from the focused tests.

If verification requires unavailable external infrastructure, an undeclared third-party dependency, or substantial repository reconstruction, stop and report the exact limitation instead of broadening scope speculatively.

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
- Do not reformat compliant files merely to produce a diff.
- Do not perform opportunistic cleanup.
- State every additionally inspected file and why it was needed.
- Add or change tests with behavior changes.
- Do not create task-history or checkpoint files unless explicitly requested.

## Verification workflow

For a complete checkout:

1. Run the narrowest relevant test file or test selection first.
2. Fix targeted failures before expanding verification.
3. Run the full test suite only when the change is cross-cutting, changes a shared contract, is being prepared for merge, or the task explicitly requires it.
4. Run formatting, lint, type, compile, or contract checks that are already configured and relevant.

For a bounded checkout:

1. Set `PYTHONPATH=src`.
2. Run focused collection first:

   ```bash
   python -m pytest <focused-test-path> --collect-only -q
   ```

3. If collection reports a missing in-repository dependency, fetch only that dependency and its necessary ancestor `__init__.py` files.
4. Retry collection.
5. Run the focused tests:

   ```bash
   python -m pytest <focused-test-path> -q
   ```

6. Run broader tests only when the task explicitly requires them or the focused change affects a documented shared contract.

Do not install or recreate the entire development environment unless a focused test proves it is necessary. Report commands and results accurately; do not claim CI or local checks that were not run.

### Release-gate verification evidence

When a task verifies a release candidate, checkpoint, or milestone:

1. Record the exact candidate commit before generating or changing any evidence file.
2. Record `git status --short` before verification and require a clean candidate tree.
3. Record the repository root, operating system, architecture, timestamp with UTC offset, Python
   version, pytest version, and Ruff version.
4. Write each exact command line into the durable artifact before its output.
5. For Ruff, capture the effective repository configuration with:

   ```bash
   python -m ruff check . --config pyproject.toml --show-settings
   ```

6. Record the real exit status of every command. Do not allow `tee` or another pipeline to hide a
   failing status.
7. Record complete pytest pass, fail, skip, xfail, and xpass counts and give every skip or expected
   failure an explicit disposition.
8. Record CLI walkthrough output and exit status; absence of CLI evidence is a blocker.
9. Distinguish an evidence file created during verification from candidate files. A dirty tree after
   evidence generation does not replace the required clean-tree record from before verification.
10. If implementation, tests, snapshots, goldens, content, configuration, or verification tooling
    changes after checks begin, invalidate the candidate and select a new exact commit.
11. Do not weaken tests, delete required fixtures, overwrite snapshots, regenerate goldens, or broaden
    lint suppressions solely to obtain a passing result.

Use `docs/PROTOTYPE_RELEASE_CHECKLIST.md` for the complete release gate and
`docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` while the Day 83 software gate remains failed.

## Close procedure

- Summarize the deliverable and files changed.
- Report verification commands and outcomes.
- State any unresolved risk or limitation.
- Record one exact next action in `CURRENT.md` when the task changes current project state; otherwise place it in the pull-request description.
- Do not append completed-task history to stable scope or architecture documents.
