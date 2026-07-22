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

- Days 1–45 are complete.
- **Day 45 — Implement the band predicate** is complete.
- Current sequential task: **Day 46 — Implement the cefepime rule**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- Four exact draft cefepime renal-dose documents remain under `src/cds/content/renal/` for the
  source-selected 500 mg every 12 hours, 1 g every 12 hours, 2 g every 12 hours, and 2 g every
  8 hours IV regimens, each administered over approximately 30 minutes.
- The content partition remains greater than `0` and less than `11`, greater than or equal to `11`
  and less than `30`, greater than or equal to `30` and less than or equal to `60`, and greater than
  `60 mL/min`.
- `src/cds/rules/predicates.py` now exposes one pure `renal_band_matches` predicate.
- The predicate receives the stored unquantized `Decimal` renal value plus explicit typed lower and
  upper `RenalContentEndpoint` objects; `None` means unbounded in that direction.
- A lower endpoint matches only when the value is greater than the endpoint or exactly equal to an
  inclusive endpoint. An upper endpoint matches only when the value is less than the endpoint or
  exactly equal to an inclusive endpoint. Both comparisons must be satisfied.
- The predicate performs no rounding, quantization, interpolation, extrapolation, unit conversion,
  input validation, content loading, eligibility determination, band selection, recommendation
  construction, or I/O.
- Focused tests prove immediately-below, at, and immediately-above behavior at the `11`, `30`, and
  `60 mL/min` boundaries, no match outside the declared greater-than-zero domain, unbounded endpoint
  behavior, and preservation of high-precision Decimal distinctions.
- No cefepime medication rule, eligibility filter, application workflow, public package import,
  serialized output contract, automatic version selection, clinical scope, or content review state
  changed.
- All source-based cefepime documents remain `review.status: draft` and remain ineligible for clinical
  rule matching until independent clinical-content review is completed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- A bounded checkout was materialized at `/tmp/cds-platform` with the focused predicate, tests, typed
  renal-content dependency, required package files, and pytest configuration.
- Pytest was available: `pytest 9.0.2`; no test dependency was installed.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_predicates.py --collect-only -q`.
- Result: `14 tests collected in 0.02s`.
- Focused test command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_predicates.py -q`.
- Result: `14 passed in 0.06s`.
- `python -m compileall -q src/cds/rules/predicates.py tests/unit/rules/test_predicates.py`
  completed successfully.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for source hierarchy, bounded-checkout rules, architectural boundaries,
  verification, and close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — required to formulate the bounded
  Day 45 prompt and identify its exact deliverable.
- `docs/SAFETY_INVARIANTS.md` — required to preserve fail-closed matching, exact boundary testing,
  auditability, and pure deterministic rule behavior.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — required for the normative endpoint semantics and prohibition
  on rounding, interpolation, extrapolation, or nearest-band selection.
- `src/cds/repositories/renal_content.py` — required because it defines the typed
  `RenalContentEndpoint` consumed by the predicate.
- `src/cds/domain/exceptions.py` — direct import required when collecting the typed renal-content
  module in the bounded checkout.
- `pyproject.toml` and required ancestor `__init__.py` files — required for focused pytest collection
  and valid package imports.

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
  integer-labeled renal bands before any document is marked reviewed.
- The reviewer must approve the provisional `guideline` evidence-level mapping for FDA-approved
  prescribing information or require a separately scoped schema change.
- The reviewer must verify the exact source transcription, monitoring text, source-unit preservation,
  and representation of approximately 30-minute administration.
- Until those requirements are complete, all four source-based cefepime documents remain draft and
  must not be matched by a clinical rule.

## Next exact action

> Day 46 — implement one pure cefepime rule that requires exact supported medication and regimen
> context, reviewed typed content at the requested immutable version, and a single renal-band match
> through `renal_band_matches`, then returns a structured recommendation retaining rule and content
> versions; draft or retired content, missing context, unsupported variants, and zero or multiple
> band matches must fail closed without a dose recommendation.
