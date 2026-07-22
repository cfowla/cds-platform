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

- Days 1–46 are complete.
- **Day 46 — Implement the cefepime rule** is complete.
- Current sequential task: **Day 47 — Handle insufficient and out-of-scope cefepime cases**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- Four exact source-based cefepime renal-dose documents remain under `src/cds/content/renal/` for the
  500 mg every 12 hours, 1 g every 12 hours, 2 g every 12 hours, and 2 g every 8 hours IV base
  regimens, each administered over approximately 30 minutes.
- All four source-based documents remain `review.status: draft` and are ineligible for rule matching
  until independent clinical-content review is completed.
- `src/cds/rules/cefepime.py` now exposes one pure `evaluate_cefepime_rule` implementation with
  implementation version `1.0.0`.
- The rule receives an already typed `MedicationOrder`, `RenalFunctionResult`, exact regimen and
  formulation identifiers, explicit renal-stability and renal-replacement-therapy facts, the exact
  requested content version, one typed `RenalDoseContent` document, and a caller-supplied evaluation
  time.
- It performs no content loading, version selection, identifier or unit normalization, dose-unit
  conversion, renal rounding, interpolation, extrapolation, fallback, I/O, or clock access.
- Eligibility requires `review.status: reviewed`, `reviewed_content_version` equal to the immutable
  document version, nonempty reviewer identity and role, and a review date. Draft and retired content
  fail closed.
- Medication, regimen, indication, route, formulation, base dose, dose unit, frequency interval,
  infusion duration, adult age, Cockcroft–Gault method, unindexed `mL/min` renal result, renal
  stability, renal-replacement-therapy status, patient identity, and requested content version must
  match exactly.
- The stored unrounded `Decimal` renal result is checked against the declared renal domain and every
  band through `renal_band_matches`; exactly one band must match.
- A successful match returns structured `RuleResult`, `CDSRecommendation`, and `DoseRecommendation`
  objects retaining the order and rule links, content and implementation versions, exact source dose
  value and unit, route, frequency, infusion duration, rationale, monitoring, evidence, provenance,
  renal result, matched band identifier, and evaluation time.
- Missing or nonexact context, ineligible review state, a version mismatch, values outside the renal
  domain, incomplete recommendation content, unresolved evidence, and zero or multiple band matches
  return no dosing recommendation.
- An explicit `no_recommendation` band is represented as an applied negative result with no
  `DoseRecommendation`; no nearest-band or substitute regimen is selected.
- No application workflow, content repository lookup, public package import, serialized output
  contract, clinical scope, content review state, or automatic version-selection policy changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- A bounded checkout was materialized at `/tmp/cds-platform` with the focused rule, tests, directly
  imported domain and repository files, required package files, and pytest configuration.
- Pytest was available: `pytest 9.0.2`; no test dependency was installed.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_cefepime.py --collect-only -q`.
- Result: `25 tests collected in 0.04s`.
- Focused test command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_cefepime.py -q`.
- Result: `25 passed in 0.06s` after the final formatting-only edits.
- `python -m compileall -q src/cds/rules/cefepime.py tests/unit/rules/test_cefepime.py`
  completed successfully.
- Ruff was not installed (`python -m ruff --version` returned `No module named ruff`); it was not
  installed or substituted.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for source hierarchy, bounded-checkout rules, architectural boundaries,
  verification, and close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — required to formulate the bounded
  Day 46 prompt and identify its exact deliverable.
- `docs/SAFETY_INVARIANTS.md` — required to preserve fail-closed exact matching, auditability, and pure
  deterministic rule behavior.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — required for exact regimen dimensions, review eligibility,
  immutable versions, band outcomes, evidence requirements, and prohibition on normalization,
  rounding, interpolation, extrapolation, or nearest-band selection.
- `src/cds/domain/clinical.py` — required because the rule consumes the existing passive
  `MedicationOrder` contract.
- `src/cds/domain/outputs.py` — required because the rule returns the existing standard renal,
  recommendation, dose-recommendation, and rule-result models.
- `src/cds/domain/enums.py`, `src/cds/domain/support.py`, and `src/cds/domain/value_objects.py` — direct
  imports required for status, evidence, provenance, coded concepts, and explicit quantities.
- `src/cds/repositories/renal_content.py` — required because it defines the typed content, exact
  regimen dimensions, review metadata, bands, recommendations, and sources consumed by the rule.
- `src/cds/rules/predicates.py` and `tests/unit/rules/test_predicates.py` — required to reuse and
  preserve the Day 45 unrounded exact-boundary predicate contract.
- `tests/unit/repositories/test_renal_content.py` — required for the established synthetic typed-content
  fixture style and exact-key/review-state conventions.
- `src/cds/content/renal/cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml` — inspected through its
  creation commit to confirm exact identifier dimensions, source-unit preservation, and draft review
  state without changing clinical content.
- `src/cds/domain/exceptions.py`, `pyproject.toml`, and required ancestor `__init__.py` files — direct
  import and focused pytest configuration dependencies in the bounded checkout.

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
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The reviewer must approve or replace the provisional continuous interpretation of the source's
  integer-labeled renal bands before any source-based document is marked reviewed.
- The reviewer must approve the provisional `guideline` evidence-level mapping for FDA-approved
  prescribing information or require a separately scoped schema change.
- The reviewer must verify the exact source transcription, monitoring text, source-unit preservation,
  and representation of approximately 30-minute administration.
- Until those requirements are complete, all four source-based cefepime documents remain draft and
  cannot produce a successful recommendation through the rule.

## Next exact action

> Day 47 — define and test explicit incomplete, unsupported, warning-bearing, and not-applicable
> cefepime outcomes for missing or out-of-scope clinical context, preserving fail-closed behavior and
> ensuring no such result contains a dose recommendation or extrapolates beyond reviewed content.
