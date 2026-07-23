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

- Days 1–55 are complete.
- **Day 55 — Add famotidine rule coverage** is complete.
- The next sequential task is **Day 56 — Weekly review: duplication audit**.

## Current state

- `src/cds/rules/famotidine.py` now exposes a medication-specific famotidine rule wrapper around the
  existing pure generic exact-regimen matcher.
- The wrapper requires exact medication, regimen, indication, oral route, film-coated-tablet
  formulation, `20 mg` dose, `12 hours` frequency, explicit null infusion duration, renal method,
  renal unit, unindexed result, stable non-RRT context, requested content version, and independently
  reviewed eligible content.
- The implementation adds only famotidine-specific identifiers, display labels, warning-code prefix,
  recommendation title, provenance source name, and implementation version; it adds no
  medication-specific engine behavior.
- Missing facts remain incomplete. Non-famotidine orders are not applicable. Unsupported regimen,
  formulation, stability, RRT, or other exact-context mismatches fail closed with no recommendation.
- Focused synthetic tests cover unrounded values immediately below and exactly at the `30` and `60
  mL/min` boundaries, structured recommendations, draft-content rejection, unsupported contexts,
  non-famotidine orders, and missing formulation.
- The source-based famotidine YAML remains draft and therefore remains ineligible for matching.
  Software verification does not confer clinical review status.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- `pytest 9.0.2` is installed in the execution environment.
- The focused pytest command could not be executed because the environment did not supply a checkout
  and the complete import closure was not locally available. No dependency was installed and no
  broad repository reconstruction was performed.
- The created rule and test files were reviewed against the existing
  `src/cds/rules/exact_renal_dose.py` contract and the established piperacillin-tazobactam wrapper and
  focused-test conventions.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/famotidine.py` — created.
- `tests/unit/rules/test_famotidine.py` — created.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 55 deliverable.
- `docs/SAFETY_INVARIANTS.md` — exact-context, fail-closed, purity, versioning, and auditability
  constraints.
- `CURRENT.md` — authoritative active task and exact acceptance context.
- `src/cds/rules/exact_renal_dose.py`, `src/cds/rules/piperacillin_tazobactam.py`, and
  `tests/unit/rules/test_piperacillin_tazobactam.py` — shared matcher contract and demonstrated wrapper
  and test conventions.
- `src/cds/rules/predicates.py` and the famotidine YAML content document — unrounded boundary semantics
  and exact famotidine identifiers, context, bands, and draft eligibility state.

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
- The selected label describes maximum renal dosages; the prototype must not imply therapy selection
  or invent an alternate formulation.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The repackaged-label source choice, exactly-`60 mL/min` boundary interpretation, provisional
  `guideline` evidence mapping, maximum-dose representation, formulation representation, source
  transcription, monitoring text, and exclusions require independent review.

## Next exact action

> Day 56 — audit cefepime, piperacillin-tazobactam, and famotidine rule implementations for only
> demonstrated duplication; preserve explicit medication content differences, remove copied logic
> where the generic exact-regimen matcher already covers it, and do not introduce speculative
> abstractions.
