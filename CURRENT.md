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
- The next sequential task is **Day 50 — Select and source piperacillin–tazobactam content**.

## Current state

- `tests/unit/rules/test_cefepime_golden_cases.py` builds seven deterministic synthetic cefepime rule
  outcomes through `evaluate_cefepime_rule()` and the canonical `dumps_json()` serializer.
- Separate committed snapshots under `examples/golden/cefepime_rule/` cover normal renal function,
  impaired renal function, the exact inclusive `30 mL/min` boundary, a missing renal value, an
  unsupported regimen, unstable renal function, and a synthetic no-recommendation contraindication
  outcome.
- Normal, impaired, and exact-boundary cases return structured successful recommendations with
  explicit decimal strings, units, renal-band identifiers, linked rule and order identifiers,
  evidence, provenance, content version, and evaluation time.
- Missing input remains `ResultStatus.INCOMPLETE`, while unsupported-regimen and unstable-renal
  cases remain warning-bearing `ResultStatus.NOT_APPLICABLE`; all three fail closed without a dose
  recommendation.
- The synthetic contraindication case uses the existing explicit `no_recommendation` band outcome,
  returns `applied=True` and `passed=False`, and produces no dose recommendation.
- Test-only review metadata is created only in the focused Python fixture. No source-based cefepime
  YAML document, persisted review metadata, clinical content, rule implementation, public contract,
  dependency, or serialization behavior changed.
- Four source-based cefepime documents remain `review.status: draft`; software tests have not made
  them clinically eligible.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- Pytest was available: `pytest 9.0.2`; no dependency was installed.
- `python -m py_compile /tmp/cds-platform/tests/unit/rules/test_cefepime_golden_cases.py` completed
  successfully after the final edit.
- The focused test file was checked for lines exceeding the configured 100-character Ruff limit;
  none remained.
- All seven locally generated JSON snapshots parsed successfully.
- GitHub blob SHA values for the focused test and all seven committed snapshots matched the locally
  generated files exactly.
- The focused pytest command was not executed because the execution environment did not provide a
  repository checkout and the connector responses were not mounted as source files for a faithful
  bounded import checkout. No source stubs, direct repository download, clone, substitute runner,
  CI, or GitHub Actions execution was used.
- No pytest, full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `tests/unit/rules/test_cefepime_golden_cases.py`
- `examples/golden/cefepime_rule/normal.json`
- `examples/golden/cefepime_rule/impaired.json`
- `examples/golden/cefepime_rule/exact_boundary.json`
- `examples/golden/cefepime_rule/missing.json`
- `examples/golden/cefepime_rule/unsupported_regimen.json`
- `examples/golden/cefepime_rule/unstable_renal_function.json`
- `examples/golden/cefepime_rule/contraindication.json`
- `CURRENT.md`

## Additional files inspected

- `AGENTS.md` — source hierarchy, bounded execution rules, architecture boundaries, verification,
  and close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and the exact
  Day 48 golden-case deliverable.
- `docs/SAFETY_INVARIANTS.md` — synthetic-data, fail-closed, auditability, and boundary-test
  requirements.
- `src/cds/rules/cefepime.py` and `tests/unit/rules/test_cefepime.py` — the exact rule API, output
  categories, no-recommendation behavior, and existing synthetic fixture conventions.
- `tests/unit/utils/test_golden_json_examples.py` — the existing per-case golden-file and canonical
  byte-comparison convention.
- `src/cds/utils/serialization.py` — deterministic JSON, decimal-string, enum, date, and UTC datetime
  serialization behavior.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/outputs.py`,
  `src/cds/domain/support.py`, and `src/cds/domain/value_objects.py` — typed input, output,
  traceability, enum, and quantity contracts imported by the focused test.
- `src/cds/repositories/renal_content.py` and `src/cds/rules/predicates.py` — typed content objects and
  exact unrounded renal-band boundary semantics used by the synthetic fixture.
- `src/cds/domain/exceptions.py` — direct repository-content import required by the focused import
  chain.
- `pyproject.toml` — pytest configuration and Ruff line-length target.

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
