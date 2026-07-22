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

- Days 1–32 are complete.
- **Day 32 — Implement the core Cockcroft–Gault calculation** is complete.
- Current sequential task: **Day 33 — Add formula tests**.

## Current state

- `cds.services.renal.calculate_cockcroft_gault` is a public, keyword-only, pure, deterministic calculator that accepts the existing typed patient, serum-creatinine result, supplied weight, weight type, evaluation date, and calculation time inputs.
- The calculator reuses `derive_age_years` and `require_supplied_weight`; it does not select, derive, normalize, convert, quantize, or presentation-round clinical inputs or outputs.
- Cockcroft–Gault arithmetic uses a local Decimal context with precision 28 and `ROUND_HALF_EVEN`, exact string-constructed constants, the male base equation, and the exact `Decimal("0.85")` female coefficient.
- The process-wide Decimal context is not changed.
- The returned `RenalFunctionResult` carries the unquantized value in exact unit `mL/min`, `normalized_to_bsa=False`, explicit patient and encounter identifiers, input snapshots, age, sex, weight type, evaluation and calculation times, and version-1 calculated provenance.
- Each call allocates a new result, value snapshots, provenance object, and safe-default collections without mutating caller-owned inputs.
- Defensive `CalculationError` checks enforce the validated-service boundary for missing required typed values, unsupported sex, nonpositive or non-Decimal serum creatinine, non-exact units, invalid supplied weight, and naive calculation time.
- The skipped calculator placeholder was replaced with focused male, female, typed-output, metadata, immutability, independent-allocation, unquantized-storage, and Decimal-context tests.
- Day 32 did not add formula matrices, fail-closed edge matrices, weight derivation, unit conversion, renal-band matching, medication rules, recommendations, orchestration, or new domain fields.

## Verification

- Focused command attempted: `PYTHONPATH=src python -m pytest tests/unit/services/test_renal.py --collect-only -q && PYTHONPATH=src python -m pytest tests/unit/services/test_renal.py -q`.
- Collection did not run because the supplied execution environment has no installed `pytest` module: `No module named pytest`.
- The focused test execution was not reached, and no Day 32 test pass is claimed.
- `git diff --check` — completed successfully with no whitespace errors.

## Additional files inspected

- `pyproject.toml` — required to reproduce repository pytest discovery, Python path, strict configuration, and declared test dependency.
- `src/cds/domain/enums.py` — required by direct service and focused-test imports for `RenalMethod`, `Sex`, and `WeightType`.
- `src/cds/domain/exceptions.py` — required by the direct service import for the existing typed `CalculationError`.
- `src/cds/domain/support.py` — required by `RenalFunctionResult` and the calculator's direct `Provenance` import.
- `src/cds/domain/value_objects.py` — required by direct service, clinical-model, output-model, and focused-test imports for `ValueWithUnit`.
- `src/cds/__init__.py`, `src/cds/domain/__init__.py`, `src/cds/services/__init__.py`, and `tests/unit/services/__init__.py` — required ancestor package markers for focused imports and collection.

## Active constraints

- Prototype-only and synthetic or properly de-identified data requirements remain unchanged.
- Structural and renal task-sufficiency validation must complete before calculation.
- Expected missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed through structured validation rather than calculator assumptions.
- The calculator remains pure and deterministic with explicit inputs, no I/O, no hidden clock, no unit conversion, and no mutable global state.
- Renal-band matching must use the stored unrounded value; display formatting remains outside the calculator.
- Clinical scope, supported medications and populations, renal method, safety behavior, clinical-content requirements, intended users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The Day 32 implementation is complete, but the focused test suite still requires execution in an environment with `pytest>=8.0` installed.

## Next exact action

> Day 33 — Add independently hand-calculated normal and impaired Cockcroft–Gault formula tests with exact unrounded expected values.
