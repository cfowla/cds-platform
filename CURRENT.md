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

- Days 1–62 are complete.
- **Day 62 — Map exceptions to structured failures** is complete.
- The next sequential task is **Day 63 — Weekly review: architecture boundary test**.

## Current state

- `src/cds/app/renal_dose.py` preserves expected clinical gaps as existing `INCOMPLETE` or
  `NOT_APPLICABLE` outcomes while converting internal failures to fail-closed `FAILED`
  `RuleResult` objects.
- `ValidationError`, `ContentNotFound`, and `CalculationError` have stable failure codes distinct
  from stage-specific unexpected repository, validation, application, calculation, and rule
  failures.
- Structured failures retain safe patient, encounter, medication, regimen, requested-content,
  content-version, rule, renal-result, and evaluation-time audit fields only when those values were
  safely available before the failure.
- Failed results set `applied=False`, `passed=None`, and contain no recommendation or alert.
- Exception messages, exception class representations, stack traces, and source payloads are not
  included in summaries or supporting data.
- A successful renal calculation is retained on an unexpected rule failure so the completed
  calculation remains auditable; failures before calculation leave the renal result absent.
- Exact medication, regimen, and content-version identifiers remain case-sensitive and are not
  normalized before repository lookup or failure mapping.

## Verification

- The execution environment did not supply a repository checkout; the required
  `git rev-parse --show-toplevel` probe reported that `/mnt/data` is not inside a Git repository.
- No filesystem search, repository clone, dependency installation, substitute runner, CI, or
  GitHub Actions investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- An import-compatible bounded verification harness was materialized at
  `/mnt/data/cds-platform-work` for the focused app module and tests. Unchanged dependencies were
  represented only as needed to satisfy the focused imports, so this is not a full-repository
  verification claim.
- The environment supplied pytest 9.0.2.
- Focused collection command:
  `python -m pytest tests/unit/app/test_renal_dose.py --collect-only -q`
- Collection result: `12 tests collected in 0.05s`.
- Focused test command:
  `python -m pytest tests/unit/app/test_renal_dose.py -q`
- Test result: `12 passed in 0.04s`.
- Compile command:
  `python -m compileall -q src/cds/app/renal_dose.py tests/unit/app/test_renal_dose.py`
- Compile result: completed with no output or error.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/app/renal_dose.py` — mapped typed and unexpected internal exceptions to structured,
  fail-closed results without exposing exception details.
- `tests/unit/app/test_renal_dose.py` — replaced deferred exception expectations with focused typed,
  unexpected, non-disclosure, audit-preservation, exact-identifier, and expected-outcome tests.
- `CURRENT.md` — replaced with the Day 62 state and Day 63 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 62 deliverable.
- `docs/SAFETY_INVARIANTS.md` — validation-before-calculation, fail-closed behavior, exact identifiers,
  content defects, purity, repository boundaries, and auditability constraints.
- `CURRENT.md` — authoritative Day 61 state and exact Day 62 action.
- `src/cds/domain/exceptions.py` — typed internal failure classes to map.
- `src/cds/domain/outputs.py` and `src/cds/validation/models.py` — standard failed-result and
  validation-state fields.
- `src/cds/app/context.py`, `src/cds/repositories/renal_content.py`, `src/cds/services/renal.py`, and
  `src/cds/rules/engine.py` — orchestration-stage contracts and available audit fields.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/support.py`, and
  `src/cds/domain/value_objects.py` — typed source objects, explicit result status, and traceability
  conventions.
- `src/cds/validation/patient.py`, `src/cds/validation/lab.py`, `src/cds/validation/renal.py`, and
  `src/cds/validation/medication.py` — expected clinical-gap behavior that must remain distinct from
  system failures.
- `src/cds/rules/registry.py` — deterministic exact-rule selection dependency imported by the engine.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structural and task sufficiency before renal calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed and produce
  no dosing recommendation.
- Medication, rule, regimen, formulation, and content-version identifiers remain exact and
  case-sensitive. Do not trim, normalize, alias, fuzzy-match, infer, or fall back.
- Do not expose exception messages, stack traces, source payloads, or unnecessary identifiers in
  structured failures.
- The use case coordinates existing components but does not duplicate validation rules, repository
  parsing, calculator formulas, rule predicates, serialization, logging, or interface behavior.
- The calculated renal result remains unrounded for rule matching and auditability.
- Draft or retired content is never eligible for clinical recommendation. Software verification does
  not confer clinical review status.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- Clinical-content source interpretations and review eligibility remain separate from this software
  orchestration task.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 63 — confirm import direction and verify that domain, services, rules, repositories, app,
> mappers, and interfaces retain their assigned responsibilities without introducing new clinical
> behavior or speculative restructuring.
