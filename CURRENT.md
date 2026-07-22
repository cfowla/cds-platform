# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available, use the GitHub connector to materialize only the named files and concretely required imports in a bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:
- repository cloning or filesystem searches for another checkout
- GitHub Actions or CI investigation
- workflow creation or modification
- web search
- PR creation, management, or merge
- broad repository review
- substitute functional test runners

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–34 are complete.
- **Day 34 — Add fail-closed edge tests** is complete.
- Current sequential task: **Day 35 — Independently verify golden renal cases and future band-boundary values**.

## Current state

- Existing structural and renal-sufficiency tests confirm that missing serum creatinine remains distinct from measured zero; invalid and nonfinite values, non-exact units, unsupported sex, missing critical facts, unstable renal function, and renal replacement therapy fail closed with error-severity validation issues and no calculation or recommendation.
- `tests/unit/services/test_renal.py` adds direct-boundary coverage for missing or malformed typed inputs, unsupported sex, invalid or nonfinite creatinine and weight values, non-exact units, unknown or malformed weight types, missing or malformed collection times, future birth dates, and naive calculation timestamps.
- Defensive failure tests verify that `CalculationError` is raised before a `RenalFunctionResult` can be constructed.
- Finite positive low and high serum-creatinine cases verify that the exact supplied Decimal is retained and used without a floor, cap, substitution, conversion, or presentation quantization.
- `cds.services.renal` now rejects nonfinite Decimal inputs without leaking raw decimal exceptions, validates required dates and timezone-aware timestamps at the calculator boundary, and translates unexpected Decimal arithmetic failures to `CalculationError`.
- The calculator remains pure and deterministic, retains the local 28-digit `ROUND_HALF_EVEN` context, and does not modify the process-wide Decimal context.
- No validation issue codes, public imports, result fields, enum values, serialization behavior, provenance contracts, clinical content, medication rules, renal bands, recommendations, orchestration, or dependencies changed.

## Verification

- `git diff --check` — completed successfully with no whitespace errors.
- Pytest execution was intentionally skipped because `pytest` is unavailable in the supplied execution environment.
- No focused-test, full-suite, or CI passing claim is made.
- Deferred command: `PYTHONPATH=src python -m pytest tests/unit/validation/test_lab.py tests/unit/validation/test_renal.py tests/unit/services/test_renal.py -q`.

## Additional files inspected

- `src/cds/__init__.py`, `src/cds/services/__init__.py`, `src/cds/validation/__init__.py`, `tests/__init__.py`, `tests/unit/__init__.py`, `tests/unit/services/__init__.py`, and `tests/unit/validation/__init__.py` — required ancestor package markers for the bounded checkout.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/exceptions.py`, `src/cds/domain/outputs.py`, `src/cds/domain/support.py`, `src/cds/domain/value_objects.py`, and `src/cds/validation/models.py` — inspected only to resolve domain types and public APIs imported by the focused service, validators, and tests.
- `pyproject.toml` — materialized to preserve the bounded repository context; no dependency was installed.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and renal task-sufficiency validation must complete before calculation.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed without a dosing recommendation.
- The calculator remains pure and deterministic with explicit typed inputs, exact Decimal arithmetic, no I/O, no hidden clock, no unit conversion, and no mutable global state.
- Do not change the process-wide Decimal context or presentation-round stored renal values.
- Renal-band matching must use the stored unrounded value; display formatting remains outside the calculator.
- Clinical scope, supported medications and populations, renal method, safety behavior, clinical-content requirements, intended users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The focused test modules still require execution in an environment with the declared test dependencies installed.

## Next exact action

> Day 35 — independently recalculate the golden renal cases, verify unrounded values used at future band boundaries, and document the verification method and limitations.
