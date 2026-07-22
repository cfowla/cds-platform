# Current Work

This file is replaced after every task. It is not an append-only diary.

## Roadmap position

- **Day 21 — Weekly review: contract tests** is complete.
- Days 1–22 are complete; Day 22 passive validation-result models were completed early.
- Current sequential task: **Day 23 — Implement structural patient validation**.

## Current state

- Focused contract tests protect representative public imports from `cds.domain.clinical`, `cds.domain.outputs`, `cds.domain.support`, `cds.domain.value_objects`, and `cds.domain.enums`.
- Every compatibility export declared by `cds.domain.models.__all__` is identity-checked against its focused-module object.
- Exact field names and ordering are protected for `RenalFunctionResult`, `Contraindication`, `DoseRecommendation`, `CDSRecommendation`, `Alert`, and `RuleResult`.
- Complete member-to-wire-value mappings are protected for `Sex`, `ResultStatus`, `RenalMethod`, `Severity`, and `WeightType`.
- Canonical serialization contracts protect Decimal precision and scale, UTC `Z` datetime normalization, nested declared field names, enum wire values, `None`/`False`/zero distinctions, deterministic mapping output, and explicit unsupported-input failures.
- The renal-shaped serialization fixture uses fixed synthetic identifiers and preserves the non-production, not-for-direct-clinical-use warning.

## Verification baseline

- `python -m pytest tests/contract/test_domain_serialization_contracts.py -q` — `32 passed in 0.07s`.
- `python -m pytest -q` — `196 passed, 23 skipped in 0.35s`.
- The 23 skips are existing, explicitly identified placeholder tests for unimplemented components; no failures or warnings were reported.

## Active constraints

- No production model, enum, serializer, golden JSON artifact, clinical content, dependency, or interface behavior was changed.
- No deserialization behavior, renal sufficiency rule, or clinical assertion was added.

## Blockers

- None.

## Next exact action

> Implement Day 23 structural patient validation for impossible dates, adult-scope facts, nonpositive anthropometrics, declared weight type, and required timezone behavior without deriving clinical values.
