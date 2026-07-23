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

- Days 1–48 are complete.
- **Day 48 — Write cefepime golden cases** is complete.
- Current sequential task: **Day 49 — Weekly review: end-to-end cefepime**.

## Current state

- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` remains the normative version 1 content contract.
- Four source-based cefepime documents remain under `src/cds/content/renal/` with
  `review.status: draft`; software validation and test fixtures have not made them clinically
  eligible.
- `src/cds/rules/cefepime.py` remains at implementation version `1.1.0`; no production rule behavior
  changed in Day 48.
- `examples/golden/cefepime/` now contains seven deterministic canonical JSON outputs generated from
  typed synthetic objects through `evaluate_cefepime_rule()` and `dumps_json()`:
  `normal`, `impaired`, `exact_boundary`, `missing`, `unsupported_regimen`,
  `unstable_renal_function`, and `contraindication`.
- The normal and exact-boundary cases preserve the exact `2 g` recommendation; the impaired case
  preserves the exact `500 mg` recommendation without hidden conversion.
- The exact-boundary fixture uses an unrounded renal value of `30 mL/min` and proves that the
  inclusive upper band is selected. The immediately-below fixture preserves
  `29.999999999999999999 mL/min` and selects the lower band without rounding.
- Missing renal data remain `null`, return `ResultStatus.INCOMPLETE`, and contain no recommendation.
- Unsupported regimen and unstable renal-function fixtures return `ResultStatus.NOT_APPLICABLE`,
  retain coded warnings, and contain no recommendation.
- The contraindication fixture uses a test-only synthetic `no_recommendation` band. It returns an
  applied negative result with `passed=False`, a matched band identifier, a coded warning, and no
  `DoseRecommendation`; it does not assert a real cefepime contraindication.
- All new fixtures identify themselves as synthetic, non-production, and not for direct clinical
  use. No patient data, production clinical guidance, source selection, reviewer identity, content
  review state, public domain model, serializer contract, interface, or supported scope changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- Pytest was available: `pytest 9.0.2`; no dependency was installed.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the focused golden
  test, committed fixtures, and the directly required import-compatible domain, repository, rule,
  predicate, and serializer contracts. Exact repository contracts were separately inspected through
  the GitHub connector.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_cefepime_golden.py --collect-only -q`.
- Result: `17 tests collected in 0.03s`.
- Focused test command:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_cefepime_golden.py -q`.
- Result: `17 passed in 0.06s`.
- `python -m compileall -q tests/unit/rules/test_cefepime_golden.py` completed successfully.
- Ruff was not installed (`python -m ruff --version` returned `No module named ruff`); it was not
  installed or substituted.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `tests/unit/rules/test_cefepime_golden.py`
- `examples/golden/cefepime/normal.json`
- `examples/golden/cefepime/impaired.json`
- `examples/golden/cefepime/exact_boundary.json`
- `examples/golden/cefepime/missing.json`
- `examples/golden/cefepime/unsupported_regimen.json`
- `examples/golden/cefepime/unstable_renal_function.json`
- `examples/golden/cefepime/contraindication.json`
- `CURRENT.md`

## Additional files inspected

- `AGENTS.md` — source hierarchy, bounded-checkout rules, import-driven expansion, architecture, and
  close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — Day 48 prompt structure,
  deliverable, coverage categories, and next sequential task.
- `docs/SAFETY_INVARIANTS.md` — synthetic-data requirement, fail-closed behavior, explicit units,
  deterministic logic, auditability, and boundary-test requirements.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — exact identifiers, unrounded renal-boundary semantics,
  explicit `no_recommendation` outcomes, and review eligibility.
- `src/cds/rules/cefepime.py` and `tests/unit/rules/test_cefepime.py` — current rule outcomes,
  synthetic typed-content pattern, warning codes, versions, and no-recommendation behavior.
- `src/cds/utils/serialization.py` and `tests/unit/utils/test_golden_json_examples.py` — canonical
  serializer behavior and existing byte-for-byte golden-fixture conventions.
- `src/cds/domain/enums.py`, `src/cds/domain/support.py`, `src/cds/domain/outputs.py`,
  `src/cds/domain/clinical.py`, and `src/cds/domain/value_objects.py` — exact typed input, output,
  warning, provenance, quantity, and missing-data contracts used by the fixtures.
- `src/cds/repositories/renal_content.py` and `src/cds/rules/predicates.py` — typed renal-content
  objects and direct unrounded interval matching required by focused collection.
- `pyproject.toml` — declared pytest and Ruff configuration.

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
- Draft or retired source content is never eligible for rule matching. Synthetic reviewed test
  content does not alter clinical approval state.
- Do not invent a production reviewer identity, resolve source ambiguity silently, or treat source
  ranges as authorization for the prototype to select an initial regimen.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The reviewer must approve or replace the provisional continuous interpretation of the source's
  integer-labeled renal bands before any source-based document is marked reviewed.
- The reviewer must approve the provisional `guideline` evidence-level mapping for FDA-approved
  prescribing information or require a separately scoped schema change.
- Until review is complete, all four source-based cefepime documents remain draft and cannot produce
  a successful recommendation through the production content path.

## Next exact action

> Day 49 — add focused integration coverage that runs structural and sufficiency validation through
> renal calculation, typed content retrieval, cefepime rule matching, and standard result assembly
> using synthetic reviewed test content while preserving all source-based cefepime content as draft.
