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

- Days 1–49 are complete.
- **Day 49 — Weekly review: end-to-end cefepime** was completed out of sequence before Day 48.
- Day 49 was reverified after completion of the Day 48 golden-case matrix.
- The next sequential task is **Day 50 — Select and source piperacillin–tazobactam content**.

## Current state

- `tests/unit/rules/test_cefepime_golden_cases.py` and the seven committed snapshots under
  `examples/golden/cefepime_rule/` cover normal, impaired, exact-boundary, missing,
  unsupported-regimen, unstable-renal-function, and synthetic contraindication outcomes.
- `tests/integration/test_cefepime_end_to_end.py` composes structural and sufficiency validation,
  pure Cockcroft–Gault calculation, YAML content loading, exact cefepime rule matching, draft-content
  ineligibility, and canonical serialization.
- Combined verification exposed that an exact calculated value numerically equal to `50` could retain
  the Decimal representation `5E+1`, causing the Day 49 wire-value assertions to receive `"5E+1"`
  instead of `"50"`.
- `calculate_cockcroft_gault()` now converts the already calculated Decimal through fixed-point text
  and back to Decimal before storing it. This changes representation only; it does not round,
  quantize, cap, floor, or otherwise change the numeric value used for renal-band matching.
- The end-to-end result now emits `"50"` consistently in both `supporting_data.renal_value` and the
  canonical serialized renal quantity.
- No clinical content, renal formula, precision context, supported population, regimen, rule
  eligibility behavior, public field, dependency, interface, or review status changed.
- Four source-based cefepime documents remain `review.status: draft`; software verification has not
  made them clinically eligible.

## Verification

- The execution environment did not provide a repository checkout.
- A network clone was attempted only because combined verification and publication were explicitly
  requested; it failed because the environment could not resolve `github.com`.
- A bounded verification checkout was reconstructed from the authoritative default-branch test files
  and their concretely required imports. No dependency was installed.
- Available tools: Python `3.13.5`, pytest `9.0.2`, and PyYAML `6.0.3`.
- The initial combined run collected six Day 48 and Day 49 tests: five passed and the successful Day 49
  integration case failed because `Decimal('5E+1')` serialized as `"5E+1"` rather than `"50"`.
- After the representation-only calculator correction, the following focused command completed with
  **15 passed**:

  `python -m pytest tests/unit/utils/test_serialization.py tests/unit/rules/test_cefepime_golden_cases.py tests/integration/test_cefepime_end_to_end.py`

- The passing set includes nine canonical serialization tests, four Day 48 golden-case tests, and two
  Day 49 end-to-end integration tests.
- The full repository suite was not run because no full checkout was available and no workflow or CI
  execution was created or used.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/services/renal.py`
- `CURRENT.md`

## Additional files inspected

- `CDS_12_Week_Daily_Project_Plan.html` — exact Day 48 and Day 49 deliverables.
- `tests/unit/rules/test_cefepime_golden_cases.py` and the Day 48 commits — required outcome matrix and
  deterministic snapshot conventions.
- `tests/integration/test_cefepime_end_to_end.py` — Day 49 validation-through-serialization contract.
- `tests/unit/utils/test_serialization.py` and `src/cds/utils/serialization.py` — Decimal precision,
  scale, and canonical wire-value behavior.
- `src/cds/rules/cefepime.py` — renal supporting-data representation and exact band matching.
- `src/cds/services/renal.py` — source of the exponent-form Decimal representation.
- The domain, validation, repository, predicate, and synthetic YAML imports directly required by the
  focused tests — bounded reconstruction and execution only.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, indication, route, formulation, dose, frequency, infusion-duration,
  renal-unit, renal-method, and content-version keys are matched without aliases, normalization,
  fuzzy matching, interpolation, extrapolation, fallback, or automatic version selection.
- Clinical decimal values and units remain explicit; renal-band matching uses the stored unrounded
  value.
- No hidden `mg`/`g` conversion or equivalence comparison is authorized.
- Draft or retired content is never eligible for rule matching. Software validation does not confer
  clinical review status.
- Synthetic test-only review metadata must remain confined to transient test objects and must not be
  represented as actual clinical review.
- Do not invent a real reviewer identity, resolve source ambiguity silently, or treat source ranges
  as authorization for the prototype to select an initial regimen.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The reviewer must approve or replace the provisional continuous interpretation of the cefepime
  source's integer-labeled renal bands before any source-based document is marked reviewed.
- The reviewer must approve the provisional `guideline` evidence-level mapping for FDA-approved
  prescribing information or require a separately scoped schema change.
- Until review is complete, all four source-based cefepime documents remain draft and cannot produce
  a successful recommendation through the rule.

## Next exact action

> Day 50 — select and source piperacillin–tazobactam content by documenting exact medication and
> regimen identifiers, the authoritative source and version, supported indications, standard and
> extended-infusion variants, renal bands, ambiguities, limitations, and required reviewer metadata
> without encoding content or implementing rule behavior.
