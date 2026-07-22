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

- Days 1–35 are complete.
- **Day 35 — Independently verify golden renal cases and future band-boundary values** is complete.
- Current sequential task: **Day 36 — Design the renal-dose YAML schema**.

## Current state

- Four synthetic golden Cockcroft–Gault cases were independently recalculated from exact integer ratios, then converted at the specification's 28-significant-digit `ROUND_HALF_EVEN` operation boundaries.
- The verification record distinguishes the female calculation's required two-step Decimal evaluation from a one-step exact-fraction rounding; the implementation matches the normative `base_crcl` then `× 0.85` sequence.
- A focused synthetic threshold triplet proves that immediately-below, exact, and immediately-above values remain distinct in stored form even though all three would display as `60.0` at one decimal place.
- `docs/RENAL_CALCULATOR_VERIFICATION.md` records the method, exact fractions, fixed expected values, boundary evidence, and limitations.
- `docs/RENAL_CALCULATOR_SPEC.md` links the verification record without changing the calculation contract.
- No calculator logic, validation behavior, public import, domain model, result field, enum value, serialization behavior, clinical content, renal band, medication rule, recommendation, interface, or dependency changed.

## Verification

- Independent exact-rational reference script — completed successfully: `7 independent reference values verified with specified operation boundaries`.
- `python -m py_compile tests/unit/services/test_renal.py` — completed successfully.
- `git diff --cached --check` in the bounded checkout — completed successfully with no whitespace errors.
- Pytest execution was intentionally skipped because `pytest` is unavailable in the supplied execution environment.
- No focused-test, full-suite, or CI passing claim is made.
- Deferred command: `PYTHONPATH=src python -m pytest tests/unit/services/test_renal.py -q`.

## Additional files inspected

- None. The bounded Day 35 files were sufficient.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and renal task-sufficiency validation must complete before calculation.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed without a dosing recommendation.
- The calculator remains pure and deterministic with explicit typed inputs, exact Decimal arithmetic, no I/O, no hidden clock, no unit conversion, and no mutable global state.
- Do not change the process-wide Decimal context or presentation-round stored renal values.
- Future renal-band matching must use the stored unrounded value; display formatting remains outside the calculator.
- Clinical scope, supported medications and populations, renal method, safety behavior, clinical-content requirements, intended users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- The focused test module still requires execution in an environment with the declared test dependencies installed.
- Actual band-selection verification remains deferred until a renal-band predicate and versioned clinical content exist.

## Next exact action

> Day 36 — define the renal-dose YAML schema with exact medication and regimen identifiers, explicit inclusive and exclusive renal-band boundaries, dosing fields, supported context, sources, versions, reviewer metadata, and limitations for the three frozen-scope medications.

