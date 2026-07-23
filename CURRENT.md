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

- Days 1–56 are complete.
- **Day 56 — Weekly review: duplication audit** is complete.
- The next sequential task is **Day 57 — Define the evaluation context**.

## Current state

- `src/cds/rules/cefepime.py` is now a thin medication-specific wrapper around the existing pure
  `evaluate_exact_renal_dose_rule` matcher, consistent with the piperacillin-tazobactam and
  famotidine wrappers.
- Cefepime-specific identifiers, display text, warning-code prefix, recommendation title,
  provenance source name, and implementation version remain explicit in `ExactRenalDoseRuleConfig`.
- The duplicated cefepime matching, fail-closed outcome, recommendation construction, evidence,
  provenance, and band-selection logic was removed rather than abstracted again.
- Medication and regimen content differences remain in versioned content and wrapper configuration;
  no speculative rule hierarchy, registry, DSL, normalization, conversion, or inference was added.
- Public exports and the existing cefepime implementation version remain unchanged.

## Verification

- No repository checkout was supplied to this connector-backed execution, so no local command was
  run and no filesystem search or clone was attempted.
- The updated cefepime wrapper was reviewed directly against `src/cds/rules/exact_renal_dose.py`,
  `src/cds/rules/piperacillin_tazobactam.py`, `src/cds/rules/famotidine.py`, and the focused cefepime
  test imports.
- The intended focused command is:
  `python -m pytest tests/unit/rules/test_cefepime.py tests/unit/rules/test_piperacillin_tazobactam.py tests/unit/rules/test_famotidine.py`
- If `pytest` is unavailable in a supplied checkout environment, skip that command without installing
  it and report the limitation.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/cefepime.py` — replaced the copied matching engine with a thin shared-matcher wrapper.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 56 deliverable.
- `docs/SAFETY_INVARIANTS.md` — fail-closed, exact-context, purity, versioning, and auditability
  constraints.
- `CURRENT.md` — authoritative active task and completion context.
- `src/cds/rules/exact_renal_dose.py` — demonstrated shared implementation already covering the
  duplicated cefepime behavior.
- `src/cds/rules/piperacillin_tazobactam.py` and `src/cds/rules/famotidine.py` — established thin-wrapper
  pattern.
- `tests/unit/rules/test_cefepime.py` — confirmed the focused public imports and test boundary.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before calculation or matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed without a
  dosing recommendation.
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
  duplication audit.

## Next exact action

> Day 57 — create one typed evaluation context containing only the validated facts required by renal
> calculation and exact medication-regimen evaluation; do not move validation, content loading,
> calculation, or rule behavior into the context object.
