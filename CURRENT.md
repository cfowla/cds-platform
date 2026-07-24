# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:
- repository cloning or filesystem searches for another checkout
- GitHub Actions or CI investigation
- workflow creation or modification
- broad repository review
- substitute functional test runners

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–63 are complete.
- **Day 63 — Weekly review: architecture boundary test** is complete.
- The next sequential task is **Day 64 — Define the CLI request DTO**.

## Current state

- `tests/contract/test_architecture_boundaries.py` recursively parses Python imports under
  `src/cds/` with the standard-library `ast` module.
- The test verifies that all documented layer directories remain present and that internal imports
  follow the dependency direction defined in `ARCHITECTURE.md`.
- The test also rejects direct file, serialization, network, subprocess, database, and YAML imports
  from the passive domain layer and the pure services and rules layers.
- `RenalDoseEvaluationContext` is now canonically defined in `src/cds/rules/context.py`.
- `src/cds/app/context.py` remains a compatibility export, preserving the existing public import.
- `src/cds/rules/interface.py` and `src/cds/rules/engine.py` no longer import from `cds.app`.
- No calculation, validation, content, rule-matching, result, identifier, serialization, or
  fail-closed behavior changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/mnt/data` and reported that
  the directory is not inside a Git repository.
- No filesystem search, repository clone, dependency installation, substitute runner, CI, or
  GitHub Actions investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the edited files,
  the new contract test, and the architecture layer directories required by the focused test.
- The environment supplied pytest 9.0.2.
- Focused collection command:
  `python -m pytest tests/contract/test_architecture_boundaries.py --collect-only -q`
- Collection result: `3 tests collected in 0.01s`.
- Focused test command:
  `python -m pytest tests/contract/test_architecture_boundaries.py -q`
- Test result: `3 passed in 0.05s`.
- Compile command:
  `python -m compileall -q src/cds/app/context.py src/cds/rules/context.py src/cds/rules/interface.py src/cds/rules/engine.py tests/contract/test_architecture_boundaries.py`
- Compile result: completed with no output or error.
- The bounded checkout did not contain every repository Python file, so the local architecture scan
  is not a full-repository verification claim. In a complete checkout, the committed test scans
  every Python file under `src/cds/`.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/context.py` — added the canonical passive rule-evaluation context.
- `src/cds/app/context.py` — retained the former import path as a compatibility export.
- `src/cds/rules/interface.py` — removed the rules-to-app dependency.
- `src/cds/rules/engine.py` — removed the rules-to-app dependency.
- `tests/contract/test_architecture_boundaries.py` — added executable dependency and purity checks.
- `CURRENT.md` — replaced with the Day 63 state and Day 64 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and roadmap text.
- `AGENTS.md` — source hierarchy, execution constraints, boundaries, and close procedure.
- `docs/SAFETY_INVARIANTS.md` — ordering, purity, repository, and auditability constraints.
- `CURRENT.md` — authoritative Day 62 state and Day 63 action.
- `ARCHITECTURE.md` — dependency direction and module responsibilities.
- `src/cds/app/renal_dose.py` — application orchestration imports and responsibilities.
- `src/cds/repositories/renal_content.py` — typed content and repository boundary.
- `src/cds/services/renal.py` — pure calculator dependencies.
- `src/cds/utils/serialization.py` — serialization boundary.
- `tests/unit/app/test_context.py` — compatibility import and passive context contract.
- `pyproject.toml` — pytest configuration and declared dependencies.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers exact and case-sensitive; do not normalize, infer, alias, or fall back.
- Keep domain models passive, services and rules pure, repositories responsible for content access,
  app modules responsible for orchestration, and mappers and interfaces free of clinical logic.
- Preserve existing public imports and serialized contracts unless a task explicitly changes them.
- Preserve unrounded calculated values for matching and auditability.

## Blockers

- A named independent content reviewer has not been identified.
- Content review eligibility remains separate from this software architecture task.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 64 — define the minimal synthetic CLI request DTO for age or evaluation date, sex, stable serum
> creatinine, supplied weight and weight type, exact medication and regimen facts, and explicit
> evaluation time without adding mapping, interface, or decision logic.
