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
- web search
- PR creation, management, or merge
- broad repository review
- substitute functional test runners

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–36 are complete.
- **Day 36 — Design the renal-dose YAML schema** is complete.
- Current sequential task: **Day 37 — Create the first cefepime content fixture**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` is the normative version 1 YAML content contract for one
  exact medication-and-regimen pair at one content version.
- The exact first-slice medication identifiers are `cefepime`, `piperacillin_tazobactam`, and
  `famotidine`; regimen and related identifiers must be explicit, case-sensitive, and exact.
- The schema defines closed mappings, quoted Decimal strings, explicit quantities and units,
  supported-context fields, renal-domain and band structures, recommendation and
  no-recommendation outcomes, source references, content versions, review states, reviewer
  metadata, and limitations.
- Renal bands use the stored unquantized Cockcroft–Gault value in `mL/min` and must form one
  ordered, gap-free, non-overlapping partition of the declared renal domain with exactly one owner
  of every shared boundary.
- Medication-specific regimens, indications, formulations, doses, infusion strategies, renal
  cutoffs, sources, reviewer identity, and limitations remain intentionally unresolved.
- No clinical content fixture, YAML parser, dependency, typed content model, validator,
  repository, matcher, rule, recommendation, public import, domain contract, serialization
  behavior, or interface was added or changed.

## Verification

- `python -m py_compile` was not applicable because Day 36 changes documentation only.
- A standard-library schema-contract marker check completed successfully:
  `Day 36 schema contract markers verified: 9`.
- `git diff --check` in the bounded checkout — completed successfully with no whitespace errors.
- Pytest execution was intentionally skipped because `pytest` is unavailable in the supplied
  execution environment and Day 36 adds no executable test target.
- No focused-test, full-suite, or CI passing claim is made.

## Additional files inspected

- `PROJECT_CHARTER.md` — required because this task defines a clinical-content contract.
- `FIRST_VERTICAL_SLICE.md` — required to preserve the frozen three-medication and fail-closed
  feature scope.
- `ARCHITECTURE.md` — required to keep YAML parsing in repositories and content separate from
  services and rules.
- `BACKLOG.md` — required to distinguish schema decisions resolved now from medication-specific
  clinical decisions that remain open.
- `docs/RENAL_CALCULATOR_SPEC.md` — required to define matching against the stored unquantized
  Cockcroft–Gault value and exact `mL/min` unit.
- `docs/DOMAIN_CONVENTIONS.md`, `src/cds/domain/outputs.py`, and `src/cds/domain/support.py` —
  required to align Decimal, unit, recommendation, evidence, provenance, and review-facing field
  semantics with implemented contracts.
- `pyproject.toml` — inspected to confirm that no YAML dependency is currently declared and none
  should be added during this design-only task.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication and regimen facts are matched without aliases, normalization, fuzzy matching,
  interpolation, extrapolation, or fallback.
- Content defects prevent a document from becoming usable and are not silently repaired.
- Clinical decimal values and units remain explicit; renal-band matching uses the stored
  unquantized value.
- Draft or retired content is never eligible for rule matching.
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- Medication-specific source selection, regimen variants, renal bands, and reviewer identity are
  deliberately deferred to the scheduled clinical-content tasks.
- Pytest remains unavailable in the supplied execution environment.

## Next exact action

> Day 37 — create one clearly labeled non-production cefepime YAML fixture that conforms to
> `docs/RENAL_DOSE_CONTENT_SCHEMA.md`, uses an exact draft regimen identifier, contains explicit
> supported context and review status, and does not present unreviewed values as approved clinical
> guidance.
