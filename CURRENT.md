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

- Days 1–29 are complete.
- **Day 29 — Write the renal-calculator specification** is complete.
- Current sequential task: **Day 30 — Resolve age input and implement age handling**.

## Current state

- `docs/RENAL_CALCULATOR_SPEC.md` is the normative contract for the pure adult Cockcroft–Gault calculator in the frozen first slice.
- The specification fixes the exact equation, accepted sex coefficients, 28-significant-digit local Decimal context with `ROUND_HALF_EVEN`, unquantized stored result, unrounded renal-band matching, and canonical `mL/min` output.
- The specification prohibits serum-creatinine floors or caps, implicit corrections, alternate equations, weight-method selection, unit conversion, hidden timestamps, content loading, I/O, and mutable global state.
- Exact first-slice input units remain `kg` and `mg/dL`, with case-sensitive and whitespace-sensitive matching and validation before calculation.
- Renal stability remains an explicit supplied fact: missing stability maps to incomplete evaluation, explicitly unstable renal function maps to not applicable, and neither condition invokes calculation or produces a recommendation.
- The existing `RenalFunctionResult` and traceability models carry the exact inputs, method, unquantized result, evaluation and calculation times, provenance, and implementation version; no output fields were added.
- `BACKLOG.md` now points resolved calculator-contract decisions to the specification while retaining Day 30 age handling, presentation formatting, application-level status assembly, non-calculator provenance, medication identifiers, evidence, renal-content boundaries, review, and later-feature decisions.
- No calculator, age utility, mapper, orchestrator, rule, clinical content, interface, executable source, or test was added or changed.

## Verification baseline

- `python -m pytest tests/unit/validation/test_renal.py tests/unit/services/test_renal.py -q` — `42 passed, 1 skipped in 0.07s`.
- The skip is the pre-existing Cockcroft–Gault calculator placeholder and remains unchanged.
- `git diff --check` — completed successfully with no whitespace errors.
- No failures, errors, warnings, or unexpected output were reported by the final targeted run.

## Additional files inspected

- `pyproject.toml` — required to reproduce repository pytest discovery, `pythonpath`, and strict configuration.
- `src/cds/domain/clinical.py` — required to resolve `Patient` and `LabResult` imports used by the focused renal validation tests.
- `src/cds/domain/support.py` — required to resolve traceability objects used by the focused purity and non-mutation tests.
- `src/cds/domain/value_objects.py` — required to resolve exact value-with-unit behavior used by the focused tests.
- `src/cds/validation/models.py` — required to resolve the typed validation result contract returned by the named validator.
- `tests/unit/validation/__init__.py` and `tests/unit/services/__init__.py` — required to reproduce repository package-based collection for two focused test files sharing the basename `test_renal.py`.

## Active constraints

- Prototype-only and synthetic or properly de-identified data requirements remain unchanged.
- Validation must complete successfully before calculation or rule matching.
- Expected missing, invalid, unsupported, ambiguous, and out-of-scope clinical facts fail closed through structured validation rather than calculator assumptions or exceptions.
- The future calculator remains pure and deterministic and receives only explicit validated inputs.
- Clinical scope, supported medications and populations, renal method, safety behavior, clinical-content requirements, intended users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- None for the Day 29 renal-calculator specification deliverable.

## Next exact action

> Day 30 — Resolve age input and implement age handling. Define whether the calculator receives supplied age or derives it from evaluation date and birth date; test birthdays, leap years, future dates, and reproducibility.
