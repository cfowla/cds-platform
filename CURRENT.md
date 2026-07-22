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

- Days 1–23 are complete.
- **Day 23 — Implement structural patient validation** is complete.
- Current sequential task: **Day 24 — Implement structural lab validation**.

## Current state

- `validate_patient_structure` is a pure, deterministic validator returning the existing passive `ValidationResult`.
- Evaluation time must be explicitly supplied with a usable UTC offset; birth-date checks use the calendar date represented by that aware datetime.
- Present birth dates are checked only for impossible future dates and the frozen adult boundary, accepting the exact 18th birthday.
- Present weight and height values must be finite positive `Decimal` values with nonblank units; missing numerics remain `None` and distinct from zero.
- A supplied actual-body-weight value requires an explicitly declared non-`UNKNOWN` `WeightType`; no weight type is inferred or selected.
- Findings use stable codes, error severity, specific field paths, and deterministic ordering.
- Validation does not mutate patient facts or traceability collections and does not derive age, BMI, ideal weight, adjusted weight, creatinine clearance, or another clinical value.
- No compatibility export was added because the existing public API conventions did not require editing `src/cds/validation/__init__.py`.

## Verification baseline

- `python -m pytest tests/unit/validation/test_patient.py tests/unit/validation/test_models.py -q` — `45 passed in 0.10s`.
- No errors, warnings, or unexpected output were reported in the successful focused run.
- The full suite was not run because no shared or compatibility-export file changed and targeted testing exposed no broader regression.

## Additional files inspected

- `src/cds/domain/support.py` — required to resolve the traceability imports used by `Patient` and the non-mutation test.
- `tests/unit/validation/test_models.py` — required by the specified focused verification command and to preserve passive validation-model behavior.
- `pyproject.toml` — inspected after the first isolated local collection attempt could not resolve the `src` package path; its pytest `pythonpath` setting was then reproduced for the exact rerun.

## Active constraints

- No domain model, enum, value object, passive validation model, serialization behavior, clinical content, dependency, or interface behavior was changed.
- No renal sufficiency validation, age service, unit conversion, weight-selection policy, calculation, or rule-matching behavior was added.
- Synthetic identifiers and values are used throughout focused tests; prototype-only and not-for-direct-clinical-use constraints remain unchanged.

## Blockers

- None.

## Next exact action

> Day 24 — Implement structural lab validation.
