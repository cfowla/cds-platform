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

- Days 1–37 are complete.
- **Day 37 — Create the first cefepime content fixture** is complete.
- Current sequential task: **Day 38 — Implement content schema validation**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` is the first cefepime content fixture.
- The fixture represents one exact medication-and-regimen pair with exact, case-sensitive
  identifiers, quoted clinical decimal strings, explicit units, supported-context declarations,
  a gap-free two-band renal-domain partition, source metadata, limitations, and review metadata.
- Every medication-regimen value, renal boundary, recommendation, rationale, and monitoring
  statement in the fixture is explicitly synthetic and non-clinical.
- The fixture review status is `draft`; reviewer fields are `null`, and the fixture is not eligible
  for rule matching or patient-care use.
- Authoritative cefepime source selection, final regimen identifiers, reviewed clinical values,
  reviewer identity, and approval remain unresolved for their scheduled clinical-content tasks.
- No YAML parser, dependency, typed content model, validator, repository, matcher, rule,
  recommendation behavior, public import, domain contract, serialization behavior, or interface
  was added or changed.

## Verification

- A standard-library fixture-contract marker check completed successfully:
  `Day 37 cefepime fixture markers verified: 21`.
- The marker check confirmed the prototype warning, exact cefepime and regimen identifiers, fixed
  supported context, explicit renal domain and shared boundary ownership, source metadata, draft
  review state, null reviewer fields, and absence of schema angle-bracket placeholders.
- `git diff --check` in the bounded checkout completed successfully with no whitespace errors.
- Pytest execution was intentionally skipped because `pytest` is unavailable in the supplied
  execution environment and Day 37 adds no executable Python test target.
- No YAML parser or future schema validator was used because neither is implemented or declared.
- No focused-test, full-suite, or CI passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for repository workflow, bounded-checkout, architecture, and close rules.
- `PROJECT_CHARTER.md` — required because this task adds clinical-content-shaped data.
- `FIRST_VERTICAL_SLICE.md` — required to preserve the frozen medication, population, renal-method,
  and fail-closed scope.
- `ARCHITECTURE.md` — required to place data-only content under `src/cds/content/` and avoid parser
  or rule logic in the fixture.
- `BACKLOG.md` — required to preserve unresolved source, regimen, renal-band, and reviewer decisions.
- `src/cds/content/__init__.py` — inspected to confirm the existing content package boundary.

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

- The fixture cannot be machine-validated until the Day 38 schema validator and required YAML
  loading boundary exist.
- Medication-specific authoritative source selection, final supported variants, reviewed renal
  bands, and reviewer identity remain deliberately deferred.
- Pytest remains unavailable in the supplied execution environment.

## Next exact action

> Day 38 — implement content schema validation that rejects missing or unknown keys, wrong types,
> invalid units or identifiers, non-string clinical decimals, unsupported context, malformed or
> gapped renal bands, contradictory outcomes, unresolved sources, and invalid review metadata,
> with focused tests against the Day 37 synthetic fixture and deliberately invalid variants.
