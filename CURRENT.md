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
- **Day 49 — Weekly review: end-to-end cefepime** was completed out of sequence as explicitly
  requested.
- Current sequential task remains **Day 48 — Write cefepime golden cases**.

## Current state

- `tests/integration/test_cefepime_end_to_end.py` now composes the existing structural patient and
  serum-creatinine validators, renal and medication sufficiency validators, pure Cockcroft–Gault
  calculator, YAML repository, exact cefepime rule, and canonical serializer.
- The successful integration path uses only synthetic facts and derives an exact unrounded
  Cockcroft–Gault result of `50 mL/min`. This proves deterministic selection of the inclusive
  upper synthetic band.
- The successful path creates a distinct, test-only typed content version after loading the draft
  synthetic YAML fixture. It does not edit the YAML fixture, source-based cefepime documents, or any
  persisted review metadata and does not represent clinical review.
- A separate integration case loads the unchanged draft YAML content and verifies that it remains
  `ResultStatus.INCOMPLETE`, unapplied, indeterminate, and without a recommendation.
- The integration result is checked through `to_jsonable()` for the standard status, renal quantity,
  linked order, and explicit test-only content version.
- No production implementation, clinical scope, supported regimen, domain contract, rule behavior,
  content document, review state, interface, dependency, or serialization rule changed.
- Four source-based cefepime documents remain `review.status: draft`; software validation and
  testing have not made them clinically eligible.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because
  no repository checkout was present; no filesystem search or clone was attempted.
- Pytest was available: `pytest 9.0.2`; no dependency was installed.
- `python -m py_compile /tmp/cds-platform/tests/integration/test_cefepime_end_to_end.py` completed
  successfully after the final edit.
- The file was checked for lines exceeding the configured 100-character Ruff limit; none remained.
- The focused pytest command was not executed because the execution environment did not provide a
  repository checkout and the connector responses were not mounted as source files for a faithful
  bounded import checkout. No source stubs, direct repository download, clone, substitute runner,
  CI, or GitHub Actions execution was used.
- No pytest, full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `tests/integration/test_cefepime_end_to_end.py`
- `CURRENT.md`

## Additional files inspected

- `AGENTS.md` — source hierarchy, bounded execution rules, architecture boundaries, verification,
  and close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and the exact
  Day 49 end-to-end cefepime deliverable.
- `docs/SAFETY_INVARIANTS.md` — validate-before-calculate behavior, draft-content ineligibility,
  fail-closed requirements, auditability, and boundary testing.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/outputs.py`, and
  `src/cds/domain/value_objects.py` — typed input, renal-result, standard-result, enum, and
  quantity contracts required by the integration flow.
- `src/cds/validation/patient.py`, `src/cds/validation/lab.py`, `src/cds/validation/renal.py`, and
  `src/cds/validation/medication.py` — exact structural and sufficiency validation APIs.
- `src/cds/services/renal.py` — pure Cockcroft–Gault service boundary and reproducible inputs.
- `src/cds/repositories/renal_content.py`, `src/cds/repositories/yaml_renal_content.py`, and
  `tests/unit/repositories/test_renal_content_failure_matrix.py` — exact-key content loading,
  test-only in-memory replacement, and existing failure expectations.
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` — prototype-only synthetic content used
  by the integration test.
- `src/cds/rules/cefepime.py` and `tests/unit/rules/test_cefepime.py` — exact-context rule API,
  review eligibility, boundary outcome, and existing synthetic test conventions.
- `src/cds/utils/serialization.py` — canonical standard-result serialization contract.
- `tests/unit/services/test_renal.py` — existing synthetic Cockcroft–Gault input conventions.
- `pyproject.toml` — pytest configuration, PyYAML declaration, and Ruff line-length target.

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
- Synthetic test-only review metadata must remain confined to transient test objects and must not be
  represented as actual clinical review.
- Do not invent a real reviewer identity, resolve source ambiguity silently, or treat source ranges
  as authorization for the prototype to select an initial regimen.

## Blockers

- Day 48 golden-case coverage remains pending and is still the next sequential roadmap task.
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
