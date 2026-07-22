# Current Work

This file is replaced after every task. It is not an append-only diary.

## Completed

- CDS task prompt template deduplication complete.

## Current state

- `docs/TASK_TEMPLATE.md` is the single canonical CDS task prompt template.
- The duplicate root-level `CDS_TASK_PROMPT_TEMPLATE.md` has been removed.

## Relevant files

- `docs/TASK_TEMPLATE.md`

## Baseline

- Documentation-only change; no clinical logic, package structure, or runtime behavior changed.

## Blockers

- None.

## Next exact action

- Implement passive `ValidationIssue` and `ValidationResult` models in `src/cds/validation/models.py` with focused tests in `tests/unit/validation/test_models.py`; do not add renal sufficiency rules.
