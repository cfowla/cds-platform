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

- **Day 20 — Create golden JSON examples** is complete.
- Current sequential task: **Day 21 — Weekly review: contract tests**.
- Days 1–20 are complete.
- Day 22 passive validation-result models were completed early; that work does not skip Day 21.

## Current state

- Four deterministic renal-evaluation golden JSON examples are committed for complete, incomplete, unsupported, and warning-bearing results.
- Every example is reconstructed from typed domain objects with `RuleResult` at the top level.
- Every committed artifact is generated through `cds.utils.serialization.dumps_json`.
- Fixed UTC timestamps, synthetic identifiers, explicit units, Decimal strings, traceability metadata, and non-production clinical-use disclaimers are preserved.
- Incomplete and unsupported examples remain fail-closed and contain no dosing recommendation.
- Missing or unevaluated values remain `None`; explicit negative findings remain `False`.
- Focused tests protect parsing, exact-byte regeneration, determinism, status distinctions, warning structure, synthetic data, and clinical-use disclaimers.

## Verification baseline

- `python -m pytest tests/unit/utils/test_golden_json_examples.py -q` — `15 passed in 0.07s`.
- `python -m pytest -q` — `164 passed, 23 skipped in 0.35s`.
- The 23 skips are existing, explicitly identified placeholder tests for unimplemented components; no failures or warnings were reported.

## Active constraints

- No production domain model, serializer, validation, calculation, rule, clinical-content, dependency, or interface was changed.
- The examples are synthetic schema demonstrations and are not reviewed clinical guidance or for direct clinical use.

## Blockers

- None.

## Next exact action

> Implement Day 21 contract tests protecting focused-module imports, cds.domain.models compatibility exports, output field names, enum wire values, decimal strings, UTC datetimes, and explicit failure for unsupported serialization inputs.
