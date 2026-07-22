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

- Days 1–30 are complete.
- **Day 30 — Resolve age input and implement age handling** is complete.
- Current sequential task: **Day 31 — Implement supplied weight handling**.

## Current state

- `Patient.birth_date` plus an explicit caller-supplied `evaluation_date` is the only first-slice age-input API; an independently supplied integer age is not accepted.
- `cds.services.renal.derive_age_years` is a pure, deterministic public helper that returns completed calendar years without accessing the system clock or mutating caller-owned objects.
- Birthday behavior is explicit: age increments on the birthday. For a February 29 birth, age increments on February 29 in leap years and on March 1 in non-leap years.
- Structural validation continues to report a future birth date through `birth_date_after_evaluation`; defensive service-boundary enforcement raises the existing typed `CalculationError` if a future birth date reaches age derivation.
- The derived integer is the exact value later stored in `RenalFunctionResult.age_years` and used by the Cockcroft–Gault equation.
- Focused service tests cover ordinary birthday boundaries, leap-day behavior, a zero-year result at the pure boundary, future-date failure, repeatability, and input immutability.
- The existing adult structural-validation and renal task-sufficiency responsibilities remain unchanged.
- The Cockcroft–Gault equation remains unimplemented, and its placeholder test remains skipped.
- Day 30 did not add supplied-weight handling, presentation formatting, orchestration, medication rules, clinical content, or new domain fields.

## Verification baseline

- Prior Day 29 baseline: `python -m pytest tests/unit/validation/test_renal.py tests/unit/services/test_renal.py -q` — `42 passed, 1 skipped in 0.07s`.
- Day 30 targeted command attempted: `python -m pytest tests/unit/services/test_renal.py tests/unit/validation/test_patient.py tests/unit/validation/test_renal.py -q`.
- The Day 30 targeted tests did not run because the supplied execution environment has no installed `pytest` module: `No module named pytest`.
- No Day 30 test pass is claimed. The Cockcroft–Gault placeholder remains marked with its pre-existing skip.
- `git diff --check` — completed successfully with no whitespace errors.

## Additional files inspected

- `pyproject.toml` — required to reproduce repository pytest discovery, `pythonpath`, and strict configuration.
- `src/cds/domain/clinical.py` — required to resolve `Patient` and `LabResult` imports used by the focused validation tests.
- `src/cds/domain/enums.py` — required to resolve `Sex` and `WeightType` imports used by the focused validation tests.
- `src/cds/domain/support.py` — required to resolve traceability objects used by the focused non-mutation tests.
- `src/cds/domain/value_objects.py` — required to resolve exact value-with-unit behavior used by the focused tests.
- `src/cds/validation/models.py` — required to resolve the typed validation result contract returned by the named validators.
- `tests/unit/validation/__init__.py` and `tests/unit/services/__init__.py` — required to reproduce repository package-based collection for two focused test files sharing the basename `test_renal.py`.

## Active constraints

- Prototype-only and synthetic or properly de-identified data requirements remain unchanged.
- Validation must complete successfully before age derivation, calculation, or rule matching.
- Expected missing, invalid, unsupported, ambiguous, and out-of-scope clinical facts fail closed through structured validation rather than calculator assumptions or exceptions.
- Renal helpers and the future calculator remain pure and deterministic and receive only explicit validated inputs.
- Clinical scope, supported medications and populations, renal method, safety behavior, clinical-content requirements, intended users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The Day 30 implementation is complete, but the targeted test suite still requires execution in an environment with `pytest>=8.0` installed.

## Next exact action

> Day 31 — Implement supplied weight handling. Require a supplied kilogram value and explicit `WeightType`; do not derive ideal or adjusted weight or silently select a weight method in the first slice.
