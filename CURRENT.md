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

- Days 1–31 are complete.
- **Day 31 — Implement supplied weight handling** is complete.
- Current sequential task: **Day 32 — Implement the core Cockcroft–Gault calculation**.

## Current state

- `cds.services.renal.require_supplied_weight` is a public, pure, deterministic helper for already-validated supplied body weight.
- The helper requires a positive `Decimal` value, the exact case-sensitive and whitespace-sensitive unit `"kg"`, and an explicit supported `WeightType` of `ACTUAL`, `IDEAL`, `ADJUSTED`, or `OTHER`.
- Missing, non-`Decimal`, zero, negative, non-exact-unit, unknown, missing, and invalid weight-type values raise the existing typed `CalculationError` as defensive enforcement of the validated-service boundary.
- The helper preserves the exact supplied `Decimal` representation, unit, and declared weight type without derivation, selection, conversion, normalization, quantization, rounding, or mutation.
- Each call returns a newly allocated `ValueWithUnit`; the caller-owned input is never returned directly or modified.
- Focused tests cover all supported weight types, exact `Decimal("72.40")` preservation, exact kilogram-unit retention, input immutability, independent allocation, repeatability, and all specified defensive failures.
- `cds.services.renal.derive_age_years` and its existing Day 30 behavior remain unchanged.
- The Cockcroft–Gault equation remains unimplemented, and its placeholder test remains skipped.
- Day 31 did not add weight derivation, unit conversion, output construction, presentation formatting, orchestration, medication rules, clinical content, or new domain fields.

## Verification

- Targeted command attempted: `python -m pytest tests/unit/services/test_renal.py tests/unit/validation/test_renal.py -q`.
- The targeted tests did not run because the supplied execution environment has no installed `pytest` module: `No module named pytest`.
- No Day 31 test pass is claimed.
- The pre-existing Cockcroft–Gault placeholder remains marked with its expected skip.
- `git diff --check` — completed successfully with no whitespace errors.

## Additional files inspected

- `pyproject.toml` — required to reproduce repository pytest discovery, `pythonpath`, and strict configuration.
- `src/cds/domain/clinical.py` — required to resolve `Patient` and `LabResult` imports used by the focused validation tests.
- `src/cds/domain/support.py` — required to resolve traceability objects used by the focused non-mutation test.
- `src/cds/validation/models.py` — required to resolve the typed validation result contract returned by the named validator.
- `src/cds/__init__.py`, `src/cds/domain/__init__.py`, `src/cds/services/__init__.py`, and `src/cds/validation/__init__.py` — required ancestor package markers for focused imports.
- `tests/unit/services/__init__.py` and `tests/unit/validation/__init__.py` — required to reproduce package-based collection for the two focused test files sharing the basename `test_renal.py`.

## Active constraints

- Prototype-only and synthetic or properly de-identified data requirements remain unchanged.
- Validation must complete successfully before weight handling, calculation, or rule matching.
- Expected missing, invalid, unsupported, ambiguous, and out-of-scope clinical facts fail closed through structured validation rather than calculator assumptions or exceptions.
- Renal helpers and the future calculator remain pure and deterministic and receive only explicit validated inputs.
- Unknown numeric values remain `None`, never zero.
- Clinical scope, supported medications and populations, renal method, safety behavior, clinical-content requirements, intended users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The Day 31 implementation is complete, but the targeted test suite still requires execution in an environment with `pytest>=8.0` installed.

## Next exact action

> Day 32 — Implement the core Cockcroft–Gault calculation. Return a typed unindexed `RenalFunctionResult` in `mL/min` using the exact validated age, sex, supplied weight, weight type, serum creatinine, explicit evaluation date, and timezone-aware calculation time required by `docs/RENAL_CALCULATOR_SPEC.md`.
