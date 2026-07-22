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

- Days 1–42 are complete.
- **Day 42 — Weekly review: content failure tests** is complete.
- Current sequential task: **Day 43 — Select and source cefepime content**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- `src/cds/repositories/renal_content_schema.py` continues to validate YAML text or parsed mappings
  without file I/O, normalization, repair, typed conversion, or eligibility decisions.
- `src/cds/repositories/renal_content.py` continues to define immutable typed renal-dose content,
  exact versioned keys, the runtime-checkable repository protocol, and the deterministic in-memory
  implementation.
- `src/cds/repositories/yaml_renal_content.py` continues to read explicitly supplied YAML files,
  validate them before typed conversion, reject duplicate exact keys, and retrieve only exact
  case-sensitive `(medication_id, regimen_id, content_version)` keys.
- `tests/unit/repositories/test_renal_content_failure_matrix.py` now provides one focused Day 42
  matrix across schema validation and both repository implementations.
- The matrix covers missing schema keys and supplied files, malformed YAML, duplicate mapping keys,
  invalid units, renal-band gaps and overlaps, duplicate exact repository keys, unsupported regimen
  lookups, content-version mismatches, and reviewed-version metadata mismatches.
- The matrix verifies that schema defects raise `ContentSchemaError`, absent files or exact keys raise
  `ContentNotFound`, and duplicate exact keys raise `ValueError` rather than being overwritten.
- Draft content remains explicitly represented and retrievable by repositories; no review-eligibility
  filtering, rule matching, fallback, automatic version selection, or recommendation behavior was
  added.
- No production implementation, public import, clinical scope, serialized contract, content fixture,
  or repository behavior changed.

## Verification

- Focused collection completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_renal_content_failure_matrix.py --collect-only -q`
- Result: `19 tests collected in 0.04s`.
- Focused command completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_renal_content_failure_matrix.py -q`
- Result: `19 passed in 0.17s`.
- `python -m compileall -q src/cds/repositories tests/unit/repositories/test_renal_content_failure_matrix.py`
  completed successfully.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for repository workflow, bounded-checkout, architecture, verification, and
  close rules.
- `docs/SAFETY_INVARIANTS.md` — required to preserve fail-closed content behavior and repository
  boundaries.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — required to formulate the bounded
  Day 42 task and identify its exact roadmap deliverable.
- `src/cds/repositories/renal_content_schema.py` and
  `tests/unit/repositories/test_renal_content_schema.py` — required to identify existing schema
  failures and the uncovered malformed-YAML review case.
- `src/cds/repositories/renal_content.py` and
  `tests/unit/repositories/test_renal_content.py` — required to preserve exact-key, duplicate-key,
  version-selection, and review-state contracts for the in-memory repository.
- `src/cds/repositories/yaml_renal_content.py` and
  `tests/unit/repositories/test_yaml_renal_content.py` — required to preserve file-boundary,
  schema-propagation, exact-key, and duplicate-key behavior for the YAML repository.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` — existing prototype-only draft fixture used
  by the focused matrix; it was not changed.
- `src/cds/domain/exceptions.py`, `src/cds/repositories/__init__.py`,
  `src/cds/domain/__init__.py`, and `src/cds/__init__.py` — direct imports and ancestor package files
  required by the bounded verification checkout; none were changed.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, and content-version keys are matched without aliases, normalization,
  fuzzy matching, interpolation, extrapolation, fallback, or automatic version selection.
- Duplicate exact repository keys are rejected rather than overwritten.
- Content defects prevent a document from becoming usable and are not silently repaired.
- Clinical decimal values and units remain explicit; renal-band matching will use the stored
  unquantized value.
- Draft or retired content is never eligible for rule matching, but repositories only preserve review
  state and do not decide eligibility.
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- Medication-specific authoritative source selection, final supported variants, reviewed renal
  bands, and reviewer identity remain deliberately deferred to the next content tasks.
- No content-eligibility policy, renal-band matcher, medication rule, or recommendation behavior has
  been implemented.
- The current synthetic cefepime YAML document remains draft, invented test content and is not
  clinical guidance.

## Next exact action

> Day 43 — select and source cefepime content by recording the authoritative source and version,
> supported indications and regimens, exact identifiers, renal bands, ambiguities, and required
> reviewer metadata without yet encoding unreviewed clinical recommendations as usable content.
