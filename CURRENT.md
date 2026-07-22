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

- Days 1–27 are complete.
- **Day 27 — Add typed exceptions** is complete.
- Current sequential task: **Day 28 — Weekly review: validation matrix**.

## Current state

- `ValidationError`, `ContentNotFound`, and `CalculationError` are passive, minimal, distinct `Exception` subtypes defined in `src/cds/domain/exceptions.py`.
- Each class preserves ordinary Python exception messages and `args` without custom constructors, fields, serialization, logging, or I/O.
- The exception classes are available by direct import from `cds.domain.exceptions` only; no compatibility export was added.
- Focused tests prove that each class imports, is an `Exception`, can be raised and caught by its exact type, preserves its message and `args`, and remains distinct from the other exception types.
- Expected clinical gaps remain represented through structured validation and result states; no validator, service, rule, repository, mapper, use case, or interface was changed to raise these exceptions.

## Verification baseline

- `python -m pytest tests/unit/domain/test_exceptions.py -q` — `4 passed in 0.03s`.
- Zero skipped tests, errors, warnings, or unexpected output were reported.
- The full suite was not run because no shared public import, compatibility contract, package structure, or additional shared implementation file changed.

## Additional files inspected

- `pyproject.toml` — required to reproduce the repository pytest `pythonpath` and strict test configuration while running the exact targeted command in the local checkout.

## Active constraints

- Prototype-only and synthetic or properly de-identified data requirements remain unchanged.
- Expected missing, invalid, unsupported, ambiguous, or indeterminate clinical inputs continue to fail closed through structured validation or result objects rather than exceptions.
- Clinical scope, supported medications and populations, renal methods, safety behavior, clinical-content requirements, intended users, interfaces, and the frozen renal feature contract remain unchanged.
- No clinical logic, validation logic, exception handling at application or interface boundaries, error serialization, logging, retries, dependencies, compatibility exports, or Day 28 work was added.

## Blockers

- None.

## Next exact action

> Day 28 — Weekly review: validation matrix.
