# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

LOCAL CHECKOUT ONLY.

GitHub is the source and destination for repository files, not the execution environment.

Prohibited unless explicitly requested:
- GitHub Actions or CI investigation
- workflow creation or modification
- web search
- PR creation, management, or merge
- broad repository review
- substitute verification methods

Absence of CI is not a blocker. Perform the requested work and verification in the local checkout using only the named files and task-specified commands.

Do not describe alternative execution strategies or missing infrastructure unless they prevent local completion.

## Roadmap position

- Days 1–28 are complete.
- **Day 28 — Weekly review: validation matrix** is complete.
- Current sequential task: **Day 29 — Write the renal-calculator specification**.

## Current state

- `tests/unit/validation/test_validation_matrix.py` protects shared validation-gate contracts without adding an orchestrator or duplicating focused validator branches.
- Existing focused tests already prove representative valid, missing, invalid, unsupported, ambiguous-unit, exact-match, deterministic-ordering, independent-result, and non-mutation behavior across patient, serum-creatinine, renal-sufficiency, and medication-order validation.
- The new matrix proves that structural representability does not imply renal task sufficiency and that a noncanonical weight unit accepted as structurally representable is rejected unchanged by renal sufficiency.
- A shared critical-case matrix proves fail-closed `ValidationResult` behavior for an underage patient, unsupported laboratory status, unstable renal function, and a near-match regimen identifier, including deterministic issue codes, precise field paths, error severity, nonblank messages, equivalent results, and independent issue objects and lists.
- The adult-scope boundary now explicitly covers immediately before, exactly at, and immediately after the eighteenth-birthday boundary.
- All new fixtures use synthetic identifiers and data. No age, weight method, renal function, dose, recommendation, normalized identifier, normalized unit, converted unit, or other derived clinical value is added.
- No production validation defect was exposed, so no production file was modified.
- End-to-end prevention of calculator or rule-engine invocation remains unexercised because no real application orchestration boundary exists; that behavior must be tested when orchestration is implemented.

## Validation-matrix coverage

- **Already covered:** supported structural and sufficiency inputs; missing age source, weight facts, serum-creatinine facts, population statuses, medication and regimen identifiers, and rule-required order facts; impossible or malformed values and timestamps; unsupported populations, sex states, renal states, laboratory statuses, medication identifiers, regimen identifiers, and units; exact-unit and identifier matching; missing versus zero; positive versus nonpositive quantities; deterministic ordering; independent results; and validator purity.
- **Added:** structural-versus-sufficiency interaction coverage, cross-layer preservation and rejection of a noncanonical unit, a shared critical invalid-result contract across all four validator surfaces, and the immediately-after-adult-boundary case.

## Verification baseline

- `python -m pytest tests/unit/validation -q` — `193 passed, 3 skipped in 0.26s`.
- `python -m pytest -q` — `389 passed, 22 skipped in 0.34s`.
- Zero failures, errors, warnings, or unexpected output were reported.
- The skipped tests are pre-existing placeholder tests for unimplemented components. Three are in the validation directory and twenty-two are present repository-wide. They were not removed because deleting unrelated future-component placeholders would exceed the bounded Day 28 change. Therefore the requested zero-skip target was not met, although every executed test passed.

## Additional files inspected

- `pyproject.toml` — required to reproduce the repository pytest `pythonpath`, test discovery, and strict configuration.
- `src/cds/domain/clinical.py` — required to resolve patient, laboratory, and medication-order imports used by the validation tests.
- `src/cds/domain/enums.py` — required to resolve `Sex` and `WeightType` contracts exercised by the validation tests.
- `src/cds/domain/support.py` — required to resolve nested traceability objects used by purity and non-mutation tests.
- `src/cds/domain/value_objects.py` — required to resolve exact value-with-unit and coded-concept behavior used by the validation tests.
- `src/cds/domain/outputs.py`, `src/cds/domain/models.py`, `src/cds/domain/exceptions.py`, and `src/cds/utils/serialization.py` — required only to reconstruct and execute the complete repository test suite and resolve its existing imports.

## Active constraints

- Prototype-only and synthetic or properly de-identified data requirements remain unchanged.
- Expected missing, invalid, unsupported, ambiguous, or indeterminate clinical inputs continue to fail closed through structured validation results rather than exceptions.
- Structural validation remains separate from task-sufficiency validation.
- Exact identifiers and units remain case-sensitive and whitespace-sensitive; no inference, normalization, or conversion is performed.
- Clinical scope, supported medications and populations, renal methods, safety behavior, clinical-content requirements, intended users, interfaces, and the frozen renal feature contract remain unchanged.
- No calculator, calculation specification, rule matching, clinical content, repository, mapper, use case, application orchestrator, interface, dependency, compatibility export, workflow, pull request, or dated checkpoint file was added.

## Blockers

- None for the Day 28 validation-matrix deliverable.
- Pre-existing skipped placeholder tests prevent a literal zero-skip repository result without unrelated test-suite cleanup.

## Next exact action

> Day 29 — Write the renal-calculator specification.
