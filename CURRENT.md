# Current Work

This file is replaced after every task. It is not an append-only diary.

## Roadmap position

- Current sequential task: **Day 20 — Create golden JSON examples**.
- Days 1–18 are complete.
- Day 19 is already satisfied by the documented mapper and DTO boundaries in `ARCHITECTURE.md` and `docs/DOMAIN_CONVENTIONS.md`.
- Day 22 passive validation-result models were completed early; that work does not skip unfinished Days 20–21.

## Current state

- Passive renal, recommendation, alert, and rule-result models are implemented.
- Canonical serialization is implemented for the supported domain values.
- External dictionaries and payload-specific parsing remain outside domain models at mapper and DTO boundaries.
- No dedicated Day 20 golden-example deliverable or verification is recorded in merged pull-request history.
- The prior next action had advanced to Day 23 because Day 22 was completed early; roadmap order is now restored.

## Relevant files

- `src/cds/domain/outputs.py`
- `src/cds/utils/serialization.py`
- `tests/unit/utils/test_serialization.py`
- `ARCHITECTURE.md`
- `docs/DOMAIN_CONVENTIONS.md`
- `CDS_12_Week_Daily_Project_Plan.html`

## Baseline

- Day 18 canonical serialization is implemented and tested.
- Day 19 deserialization boundaries are defined in repository documentation.
- Day 20 is the first unfinished task in roadmap order.
- Day 21 contract-test review remains pending.
- Day 22 validation models are complete but intentionally do not advance the sequential roadmap position.

## Blockers

- None.

## Next exact action

- Implement Day 20 by creating complete, incomplete, unsupported, and warning-bearing renal-evaluation golden JSON examples using only the canonical serializer, with focused verification.
