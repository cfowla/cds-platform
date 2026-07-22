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

- Days 1–33 are complete.
- **Day 33 — Add formula tests** is complete.
- Current sequential task: **Day 34 — Add fail-closed edge tests**.

## Current state

- `cds.services.renal.calculate_cockcroft_gault` remains unchanged as the public, keyword-only, pure, deterministic Cockcroft–Gault calculator.
- `tests/unit/services/test_renal.py` now includes distinct synthetic normal and impaired male formula cases constructed from typed `Patient`, `LabResult`, and `ValueWithUnit` inputs.
- The normal case derives age 40 and compares the unrounded result directly with `Decimal("111.8827160493827160493827160")` in exact unit `mL/min`.
- The impaired case derives age 75 and compares the unrounded result directly with `Decimal("31.79783950617283950617283951")` in exact unit `mL/min`.
- Both cases use actual kilogram weights, serum creatinine in exact unit `mg/dL`, explicit evaluation dates, timezone-aware timestamps, and synthetic identifiers.
- Existing formula, typed-output, metadata, immutability, allocation, Decimal-context, age, and supplied-weight tests and assertions remain preserved.
- Day 33 did not change production behavior or add fail-closed edge cases, renal-band matching, medication rules, recommendations, validation changes, dependencies, or clinical content.

## Verification

- `git diff --check` — completed successfully with no whitespace errors.
- The focused pytest tests were intentionally not executed because `pytest` is unavailable in the supplied execution environment.
- No Day 33 passing-test claim is made.
- Run later with declared test dependencies: `PYTHONPATH=src python -m pytest tests/unit/services/test_renal.py -q`.

## Additional files inspected

- `src/cds/__init__.py`, `src/cds/services/__init__.py`, and `tests/unit/services/__init__.py` — materialized only as required ancestor package markers for the bounded checkout; no additional contract analysis was required.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and renal task-sufficiency validation must complete before calculation.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed without a dosing recommendation.
- The calculator remains pure and deterministic with explicit typed inputs, exact Decimal arithmetic, no I/O, no hidden clock, no unit conversion, and no mutable global state.
- Do not change the process-wide Decimal context or presentation-round stored renal values.
- Renal-band matching must use the stored unrounded value; display formatting remains outside the calculator.
- Clinical scope, supported medications and populations, renal method, safety behavior, clinical-content requirements, intended users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The focused test module still requires execution in an environment with the declared test dependencies installed.

## Next exact action

> Day 34 — Add fail-closed edge tests for invalid or ambiguous creatinine, unsupported sex, unstable renal function, renal replacement therapy, extreme inputs, and missing critical facts without producing a recommendation.
