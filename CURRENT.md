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

- Days 1–41 are complete.
- **Day 41 — Implement a YAML repository** is complete.
- Current sequential task: **Day 42 — Weekly review: content failure tests**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 YAML contract.
- `src/cds/repositories/renal_content_schema.py` validates YAML text or parsed mappings without file
  I/O, normalization, repair, or typed conversion.
- `src/cds/repositories/renal_content.py` continues to define immutable typed renal-dose content,
  exact versioned keys, the runtime-checkable repository protocol, and the deterministic in-memory
  implementation.
- `src/cds/repositories/yaml_renal_content.py` now defines
  `YamlRenalDoseContentRepository` as the repository boundary for explicitly supplied YAML files.
- YAML repository construction reads each supplied path once as UTF-8, parses it with the duplicate-
  key-safe loader, requires complete version 1 schema validation, converts the validated mapping
  explicitly into immutable typed content, and stores it by the exact case-sensitive
  `(medication_id, regimen_id, content_version)` key.
- Decimal strings become exact `Decimal` values, validated date strings become `date` values, lists
  become tuples, null optional values remain `None`, and declared units and identifiers are preserved
  without normalization.
- Duplicate exact keys across supplied files raise `ValueError`; a missing supplied file and an
  absent exact lookup key raise the existing `ContentNotFound`; schema defects continue to raise
  `ContentSchemaError` before content becomes usable.
- The YAML repository performs no directory discovery, globbing, aliasing, trimming, case folding,
  fallback, automatic version selection, review-eligibility filtering, clinical validation, rule
  matching, recommendation construction, or file access after construction.
- No existing typed-content model, schema-validator behavior, package-level public re-export,
  clinical scope, or serialized contract was changed.

## Verification

- Focused collection completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_yaml_renal_content.py --collect-only -q`
- Result: `11 tests collected in 0.04s`.
- Focused command completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/repositories/test_yaml_renal_content.py -q`
- Result: `11 passed in 0.13s`.
- `python -m compileall -q src/cds/repositories/yaml_renal_content.py tests/unit/repositories/test_yaml_renal_content.py`
  completed successfully.
- Ruff was not installed in the bounded environment, so no lint passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Additional files inspected

- `AGENTS.md` — required for repository workflow, bounded-checkout, architecture, verification, and
  close rules.
- `docs/SAFETY_INVARIANTS.md` — required to preserve the repository content boundary and fail-closed
  behavior.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — required to formulate the bounded
  Day 41 task and identify its exact roadmap deliverable.
- `src/cds/domain/exceptions.py` — directly imported by the repository modules and required to preserve
  `ContentNotFound` and `ValidationError` contracts.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` — the existing synthetic version 1 fixture
  used for repository integration tests; it was not changed.
- `src/cds/repositories/__init__.py`, `src/cds/domain/__init__.py`, and `src/cds/__init__.py` — required
  ancestor package files for the bounded verification checkout; none were changed.
- `pyproject.toml` — required to confirm Python, PyYAML, pytest, and Ruff configuration; it was not
  changed.

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
- Draft or retired content is never eligible for rule matching.
- Clinical scope, supported medications and populations, renal method, safety behavior, intended
  users, interfaces, public domain contracts, and serialization behavior remain unchanged.

## Blockers

- Medication-specific authoritative source selection, final supported variants, reviewed renal
  bands, and reviewer identity remain deliberately deferred.
- No content-eligibility policy, renal-band matcher, medication rule, or recommendation behavior has
  been implemented.
- The current synthetic cefepime YAML document remains draft, invented test content and is not
  clinical guidance.

## Next exact action

> Day 42 — consolidate content failure tests across schema validation and both repository
> implementations, covering missing files and keys, duplicate exact keys, malformed or invalid YAML,
> gaps, overlaps, unsupported regimen identifiers, unreviewed content, and content-version mismatch
> without adding rule matching or review-eligibility behavior.
