# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:
- repository cloning or filesystem searches for another checkout
- GitHub Actions or CI investigation
- workflow creation or modification
- broad repository review
- substitute functional test runners

External source retrieval is permitted only when a bounded clinical-content source-selection task
explicitly requires it. Use the named authoritative source and do not broaden into general web
research.

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–57 are complete.
- **Day 57 — Define the evaluation context** is complete.
- The next sequential task is **Day 58 — Implement the minimal rule interface**.

## Current state

- `src/cds/app/context.py` defines the frozen, keyword-only `RenalDoseEvaluationContext` application
  carrier.
- The context contains only validated facts required by the existing Cockcroft–Gault calculator and
  exact medication-regimen rule evaluation: patient, serum-creatinine result, supplied weight and
  type, medication order, exact regimen and formulation identifiers, renal stability and renal
  replacement therapy facts, requested content version, evaluation date, and evaluation timestamp.
- The context performs no validation, normalization, inference, content loading, calculation, rule
  matching, serialization, logging, mutation, or I/O.
- Exact values and typed domain objects are preserved for later orchestration; optional formulation
  absence remains explicit as `None`.

## Verification

- No repository checkout was supplied to this connector-backed execution, so no local command was
  run and no filesystem search or clone was attempted.
- The implementation and focused tests were reviewed directly against the current renal calculator,
  renal sufficiency validator, medication-order sufficiency validator, and exact renal-dose matcher
  signatures.
- The intended focused command is:
  `python -m pytest tests/unit/app/test_context.py`
- If `pytest` is unavailable in a supplied checkout environment, skip that command without installing
  it and report the limitation.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/app/context.py` — added the passive typed renal-dose evaluation context.
- `tests/unit/app/test_context.py` — added focused field-boundary, preservation, immutability, and
  explicit-absence tests.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 57 deliverable.
- `docs/SAFETY_INVARIANTS.md` — validation-before-computation, fail-closed, explicit-context, purity,
  and auditability constraints.
- `CURRENT.md` — authoritative active task and completion context.
- `src/cds/services/renal.py` — exact validated inputs required by Cockcroft–Gault calculation.
- `src/cds/rules/exact_renal_dose.py` — exact facts consumed by medication-regimen evaluation.
- `src/cds/validation/renal.py` and `src/cds/validation/medication.py` — confirmed which facts must be
  validated before constructing the context.
- `src/cds/domain/clinical.py` — current typed patient, laboratory, and medication-order models.
- `tests/unit/validation/test_renal.py` — focused test conventions and synthetic-data pattern.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before constructing the evaluation context.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed before
  calculation or matching and produce no dosing recommendation.
- Do not add validation, calculation, content selection, repository access, rule matching, mapping,
  serialization, or interface behavior to the context.
- Match exact medication, indication, route, formulation, dose, frequency, renal method, renal unit,
  indexing state, stability, renal replacement therapy, and content version without aliases,
  normalization, conversion, inference, interpolation, extrapolation, fallback, or automatic version
  selection.
- Preserve unrounded Decimal renal values and explicit interval ownership.
- Draft or retired content is never eligible for rule matching. Software verification does not confer
  clinical review status.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- Clinical-content source interpretations and review eligibility remain separate from this software
  context task.

## Next exact action

> Day 58 — define a minimal rule interface with an `evaluate(context, content)` contract that returns
> structured `RuleResult` values without adding registry, engine, content-loading, or interface logic.
