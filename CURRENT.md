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

- Days 1–47 are complete.
- **Day 47 — Handle insufficient and out-of-scope cefepime cases** is complete.
- Current sequential task: **Day 48 — Write cefepime golden cases**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 content contract.
- Four source-based cefepime documents remain under `src/cds/content/renal/` and remain
  `review.status: draft`; software validation has not made them clinically eligible.
- `src/cds/rules/cefepime.py` now exposes implementation version `1.1.0`.
- The exact reviewed-match path remains pure and deterministic and still returns the existing
  structured recommendation, dose, renal result, evidence, provenance, rule version, content
  version, matched band, and evaluation time.
- Every rule result now records an explicit `supporting_data.outcome_category` of
  `recommendation`, `incomplete`, `unsupported`, or `not_applicable`.
- Missing required facts return `ResultStatus.INCOMPLETE`, `applied=False`, `passed=None`, no
  warnings, and no recommendation.
- Non-cefepime orders return `ResultStatus.NOT_APPLICABLE` with outcome category
  `not_applicable` and no dose recommendation.
- Exact cefepime facts outside the reviewed regimen, population, renal method, renal unit, renal
  indexing, renal stability, renal-replacement-therapy, or renal-domain contract return
  `ResultStatus.NOT_APPLICABLE` with outcome category `unsupported`, one coded warning, and no
  recommendation.
- Renal values outside the declared content domain explicitly report that no extrapolation was
  performed.
- Draft or retired content, version mismatches, patient or encounter identity defects, and zero or
  multiple band matches remain incomplete rather than being treated as supported clinical
  negatives.
- An explicit `no_recommendation` band now returns an applied negative
  `ResultStatus.NOT_APPLICABLE` result with the matched band identifier, a coded warning, and no
  `DoseRecommendation`.
- No content loading, automatic version selection, identifier or unit normalization, dose-unit
  conversion, renal rounding, interpolation, extrapolation, fallback, I/O, or clock access was
  added.
- No clinical scope, supported medication, public domain model, content review state, or interface
  changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- Pytest was available: `pytest 9.0.2`; no dependency was installed.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the updated focused
  rule and tests plus the directly required import-compatible domain, repository, and predicate
  contracts. The exact repository contracts were separately inspected through the GitHub connector.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_cefepime.py --collect-only -q`.
- Result: `41 tests collected in 0.04s`.
- Focused test command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_cefepime.py -q`.
- Result: `41 passed in 0.07s` after the final test cleanup.
- `python -m compileall -q src/cds/rules/cefepime.py tests/unit/rules/test_cefepime.py`
  completed successfully.
- Ruff was not installed (`python -m ruff --version` returned `No module named ruff`); it was not
  installed or substituted.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/cefepime.py`
- `tests/unit/rules/test_cefepime.py`
- `CURRENT.md`

## Additional files inspected

- `AGENTS.md` — source hierarchy, execution-context rules, bounded verification, architecture, and
  close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — Day 47 prompt structure,
  deliverable, acceptance wording, and next sequential task.
- `docs/SAFETY_INVARIANTS.md` — fail-closed behavior, no fabricated facts, no unit inference, no
  extrapolation, warning traceability, and boundary-test requirements.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — exact keys, supported context, renal-domain semantics,
  explicit no-recommendation bands, review eligibility, and source requirements.
- `src/cds/domain/enums.py`, `src/cds/domain/support.py`, `src/cds/domain/outputs.py`,
  `src/cds/domain/clinical.py`, and `src/cds/domain/value_objects.py` — existing result statuses,
  warning and provenance models, rule-result contract, medication-order contract, and explicit
  quantity representation used by the rule and focused tests.
- `src/cds/rules/predicates.py` — existing unrounded exact-boundary predicate contract.
- `pyproject.toml` — pytest and Ruff configuration and line-length target.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, indication, route, formulation, dose, frequency, infusion-duration,
  renal-unit, renal-method, and content-version keys are matched without aliases, normalization,
  fuzzy matching, interpolation, extrapolation, fallback, or automatic version selection.
- Clinical decimal values and units remain explicit; renal-band matching uses the stored unquantized
  value.
- No hidden `mg`/`g` conversion or equivalence comparison is authorized.
- Pediatric, intramuscular, unstable-renal-function, renal-replacement-therapy, extended-infusion,
  continuous-infusion, and unlisted cefepime variants remain unsupported.
- Draft or retired content is never eligible for rule matching. Software validation does not confer
  clinical review status.
- Do not invent reviewer identity, resolve source ambiguity silently, or treat source ranges as
  authorization for the prototype to select an initial regimen.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The reviewer must approve or replace the provisional continuous interpretation of the source's
  integer-labeled renal bands before any source-based document is marked reviewed.
- The reviewer must approve the provisional `guideline` evidence-level mapping for FDA-approved
  prescribing information or require a separately scoped schema change.
- Until review is complete, all four source-based cefepime documents remain draft and cannot produce
  a successful recommendation through the rule.

## Next exact action

> Day 48 — add deterministic cefepime golden cases covering normal, impaired, exact-boundary,
> missing, unsupported-regimen, unstable-renal-function, and contraindication outcomes through the
> canonical serializer, without marking draft clinical content reviewed.