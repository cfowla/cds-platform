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

- Days 1–44 are complete.
- **Day 44 — Encode cefepime content** is complete.
- Current sequential task: **Day 45 — Implement the band predicate**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- Four exact draft cefepime renal-dose documents now exist under `src/cds/content/renal/` for:
  - `500 mg` IV every `12 hours` over `30 minutes`;
  - `1 g` IV every `12 hours` over `30 minutes`;
  - `2 g` IV every `12 hours` over `30 minutes`; and
  - `2 g` IV every `8 hours` over `30 minutes`.
- Every document uses immutable content version `1.0.0-draft`, the exact medication, regimen,
  indication, route, formulation, rule, source, and content identifiers selected on Day 43, and the
  complete four-column renal-maintenance matrix from the selected DailyMed SPL.
- The provisional continuous unrounded Decimal partition is encoded as greater than `0` and less
  than `11`, greater than or equal to `11` and less than `30`, greater than or equal to `30` and less
  than or equal to `60`, and greater than `60 mL/min`.
- Schema-valid band IDs use `below_11`, `crcl_11_to_below_30`, `crcl_30_to_60`, and `above_60`.
  The `crcl_` prefix is required because version 1 identifiers cannot begin with a digit; this changes
  no interval or source interpretation.
- Source display units are preserved exactly. The schema validator now accepts an independently valid
  recommendation dose unit of `mg` or `g` without requiring it to equal the base-regimen unit; it
  performs no conversion, equivalence check, normalization, or value transformation.
- Each band includes source-linked rationale, renal-function monitoring, sourced neurotoxicity
  monitoring and response text, explicit limitations, exact source metadata, and the prototype
  clinical-use prohibition.
- Every document remains `review.status: draft` with null reviewer fields and is ineligible for rule
  matching until independent clinical-content review is completed.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` remains unchanged, invented, draft, and
  structurally separate from the four source-based documents.
- No band predicate, cefepime medication rule, eligibility filter, matcher, application workflow,
  public import, serialized output contract, automatic version selection, or clinical scope changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- A bounded checkout was materialized at `/tmp/cds-platform` with only the focused implementation,
  content, package, and test files required for Day 44 verification.
- Pytest was available: `pytest 9.0.2`; no test dependency was installed.
- Focused collection completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_cefepime_content.py --collect-only -q`.
- Result: `13 tests collected in 0.03s`.
- Focused command completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_cefepime_content.py -q`.
- Result: `13 passed in 0.14s`.
- `python -m compileall -q src/cds/repositories/renal_content_schema.py tests/unit/repositories/test_cefepime_content.py`
  completed successfully.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for source hierarchy, clinical-content boundaries, bounded-checkout rules,
  verification, and close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — required to formulate the bounded
  Day 44 prompt and identify its exact deliverable.
- `docs/SAFETY_INVARIANTS.md`, `PROJECT_CHARTER.md`, and `FIRST_VERTICAL_SLICE.md` — required because
  this task encodes clinical content within the frozen renal-dose scope.
- `docs/CEFEPIME_CONTENT_SELECTION.md` — authoritative Day 43 source, identifiers, regimen variants,
  renal matrix, monitoring sections, limitations, and review requirements.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — required to preserve the version 1 shape, exact identifiers,
  interval semantics, sources, review state, and quoted clinical decimals.
- `BACKLOG.md` — required to preserve unresolved boundary, evidence-level, and independent-review
  decisions without expanding scope.
- `src/cds/repositories/renal_content_schema.py` and
  `tests/unit/repositories/test_renal_content_schema.py` — required to identify and correct the
  non-normative same-unit restriction that prevented source-faithful mixed `g` and `mg` content.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` — required to preserve the existing
  structural fixture unchanged.
- `src/cds/domain/exceptions.py` — direct validator import required by the bounded checkout.
- The selected DailyMed cefepime prescribing information — used only to confirm the already selected
  renal-maintenance matrix, approximately 30-minute IV administration, renal-function monitoring,
  and neurotoxicity warning text.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, indication, route, formulation, dose, frequency, infusion-duration,
  and content-version keys are matched without aliases, normalization, fuzzy matching,
  interpolation, extrapolation, fallback, or automatic version selection.
- Clinical decimal values and units remain explicit; renal-band matching must use the stored
  unquantized value.
- No hidden `mg`/`g` conversion or equivalence comparison is authorized by the content validator.
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
- Until those requirements are complete, all four documents remain draft and must not be matched by
  a clinical rule.

## Next exact action

> Day 45 — implement one pure, deterministic renal-band predicate that evaluates the stored
> unquantized `Decimal` Cockcroft–Gault value against explicit inclusive and exclusive interval
> endpoints, with focused immediately-below, at, and immediately-above boundary tests; do not yet
> implement the cefepime medication rule or make draft content eligible for matching.
