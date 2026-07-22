# Current Work

This file is replaced after every task. It is not an append-only diary.

## Roadmap position

- **Day 21 — Weekly review: contract tests** is implemented on the active task branch.
- Days 1–21 are complete pending repository-native verification and merge.
- Day 22 passive validation-result models were completed early.
- Next sequential task after merge: **Day 23 — Implement structural patient validation**.

## Current state

- Focused contract tests protect representative public imports from `cds.domain.clinical`, `cds.domain.outputs`, `cds.domain.support`, `cds.domain.value_objects`, and `cds.domain.enums`.
- Every compatibility export declared by `cds.domain.models.__all__` is identity-checked against its focused-module object.
- Exact field names and ordering are protected for `RenalFunctionResult`, `Contraindication`, `DoseRecommendation`, `CDSRecommendation`, `Alert`, and `RuleResult`.
- Complete member-to-wire-value mappings are protected for `Sex`, `ResultStatus`, `RenalMethod`, `Severity`, and `WeightType`.
- Canonical serialization contracts protect Decimal precision and scale, UTC `Z` datetime normalization, nested declared field names, enum wire values, `None`/`False`/zero distinctions, deterministic mapping output, and explicit unsupported-input failures.
- The renal-shaped serialization fixture uses fixed synthetic identifiers and preserves the non-production, not-for-direct-clinical-use warning.

## Verification status

- `python -m pytest tests/contract/test_domain_serialization_contracts.py -q` — `32 passed in 0.19s` in the exact focused source snapshot.
- Repository-native targeted and full-suite verification are pending on the task branch.

## Active constraints

- No production model, enum, serializer, golden JSON artifact, clinical content, dependency, or interface behavior was changed.
- No deserialization behavior, renal sufficiency rule, or clinical assertion was added.

## Blockers

- Repository-native full-suite verification remains pending.

## Next exact action

> Implement Day 23 structural patient validation for impossible dates, adult-scope facts, nonpositive anthropometrics, declared weight type, and required timezone behavior without deriving clinical values.
