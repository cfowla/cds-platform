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

- Days 1–43 are complete.
- **Day 43 — Select and source cefepime content** is complete.
- Current sequential task: **Day 44 — Encode cefepime content**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- `docs/CEFEPIME_CONTENT_SELECTION.md` now records the selected FDA-approved DailyMed source,
  source version and dates, exact cefepime identifiers, four exact IV base regimens, supported
  indication identifiers, the source renal-maintenance matrix, first-slice exclusions, unresolved
  representation issues, and required independent-review attestations.
- The selected source is the WG Critical Care cefepime-for-injection SPL with DailyMed set ID
  `5fd857e5-591f-44ca-80cf-fd903660b03c`, SPL version `17`, DailyMed record update date
  `2026-06-23`, and labeling revision stated as `10/2022`.
- The initial content set is limited to exact IV powder-for-solution maintenance regimens of
  `500 mg` every `12 hours`, `1 g` every `12 hours`, `2 g` every `12 hours`, and `2 g` every
  `8 hours`, each administered over `30 minutes` and matched only to the recorded indication IDs.
- Source renal bands remain recorded as greater than `60`, `30 to 60`, `11 to 29`, and less than
  `11 mL/min`, with the complete four-column maintenance matrix transcribed into the selection
  record.
- The candidate continuous partition for unrounded Decimal matching is documented but is not yet
  clinically approved.
- The schema's lack of a regulatory-label evidence level is documented; `guideline` is only a
  provisional mapping pending review or a separately scoped schema decision.
- `BACKLOG.md` now marks cefepime source, identifiers, variants, and source bands as partially
  resolved while preserving the remaining reviewer and representation decisions.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` remains unchanged, invented, draft, and
  ineligible for rule matching.
- No loadable cefepime clinical content, medication rule, matcher, recommendation behavior, public
  import, serialized contract, or clinical scope changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- Bounded documentation verification command completed successfully:
  `python /tmp/cds-platform/verify_day43.py`.
- Result: all required source fields, exact identifiers, four regimen records, four source renal
  bands, draft-only review state, and unchanged-synthetic-fixture constraints passed.
- No pytest command was required because this task changes source-selection documentation and
  active-state records only; no executable behavior or test contract changed.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for source hierarchy, clinical-content decisions, bounded-checkout rules,
  and close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — required to formulate the
  bounded Day 43 prompt and identify its exact deliverable.
- `docs/SAFETY_INVARIANTS.md`, `PROJECT_CHARTER.md`, and `FIRST_VERTICAL_SLICE.md` — required because
  this task selects clinical content and exact supported regimens within the frozen scope.
- `BACKLOG.md` — required to resolve the existing cefepime source, identifier, variant, boundary,
  and review decisions without expanding adjacent medication scope.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — required to preserve the version 1 identifier, source,
  renal-band, review, and exact-matching contract.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` — required to preserve its structural-only
  status and confirm it was not converted into clinical guidance.
- The selected DailyMed cefepime full prescribing information — required to verify source identity,
  indications, adult base regimens, 30-minute IV administration, Cockcroft–Gault/steady-state
  language, and the adult renal-maintenance matrix.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, indication, route, formulation, dose, frequency, infusion-duration,
  and content-version keys are matched without aliases, normalization, fuzzy matching,
  interpolation, extrapolation, fallback, or automatic version selection.
- Clinical decimal values and units remain explicit; renal-band matching uses the stored
  unquantized value.
- Pediatric, IM, unstable-renal-function, renal-replacement-therapy, extended-infusion, continuous-
  infusion, and unlisted cefepime variants remain unsupported.
- Draft or retired content is never eligible for rule matching. Software validation does not confer
  clinical review status.
- Do not invent reviewer identity, resolve source ambiguity silently, or treat source ranges as
  authorization for the prototype to select an initial regimen.
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The reviewer must approve the continuous interpretation of the integer-labeled renal bands before
  content is marked reviewed.
- The reviewer must approve the provisional `guideline` mapping for FDA-approved prescribing
  information or require a separately scoped evidence-level schema change.
- Exact sourced monitoring and warning text has not yet been authored.

## Next exact action

> Day 44 — encode the four exact cefepime documents defined in
> `docs/CEFEPIME_CONTENT_SELECTION.md`, preserving source units, the complete renal-maintenance
> matrix, explicit limitations, and `review.status: draft` until the recorded boundary,
> evidence-level, and independent-review requirements are resolved; do not modify the synthetic
> fixture into clinical content.
