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

- Days 1–61 are complete.
- **Day 61 — Create the renal-dose use case** is complete.
- The next sequential task is **Day 62 — Map exceptions to structured failures**.

## Current state

- `src/cds/app/renal_dose.py` defines `RenalDoseUseCase`, which coordinates the existing structural
  validators, renal and medication task-sufficiency validators, exact typed content repository,
  pure Cockcroft–Gault calculator, and `RenalDoseRuleEngine`.
- The use case accepts typed patient, serum-creatinine, medication-order, weight, population,
  exact regimen, formulation, content-version, and evaluation-time facts. It performs no mapping,
  serialization, interface rendering, content parsing, formula implementation, or rule matching.
- Initial validation failures return `RenalDoseUseCaseResult` with the complete typed
  `ValidationResult` and an explicit `INCOMPLETE` `RuleResult`; repository retrieval, renal
  calculation, and rule evaluation are not invoked and no recommendation is produced.
- Exact content retrieval uses the case-sensitive `(medication_id, regimen_id, content_version)`
  key without trimming, normalization, aliases, version fallback, or inference.
- After content retrieval, medication-order sufficiency is validated against the exact content
  medication and regimen requirements before renal calculation or rule evaluation.
- Successful validation constructs the frozen `RenalDoseEvaluationContext`, calculates the
  unrounded unindexed Cockcroft–Gault result through `calculate_cockcroft_gault`, passes that exact
  `RenalFunctionResult` to the engine, and assembles the standard structured result with renal,
  patient, encounter, and evaluation-time audit fields when the rule did not already provide them.
- `RenalDoseRule` and `RenalDoseRuleEngine` now receive the calculated `RenalFunctionResult`
  explicitly. The engine neither recalculates renal function nor obtains it through hidden state.
- Engine unmatched and unsupported outcomes preserve the supplied renal result while remaining
  fail closed with no recommendation.
- `ContentNotFound`, `CalculationError`, and unexpected rule failures are still allowed to propagate;
  converting them to structured failed results is intentionally reserved for Day 62.

## Verification

- The execution environment did not supply a repository checkout; the required
  `git rev-parse --show-toplevel` probe reported that `/mnt/data` is not inside a Git repository.
- No filesystem search, clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- The environment supplied pytest 9.0.2, so the focused pytest verification was executed.
- Because `/tmp` did not persist across connector/tool invocations, an import-compatible bounded
  verification harness was maintained at `/mnt/data/cds-platform-work`; GitHub remained authoritative
  for the source files and final changes.
- Focused collection command:
  `python -m pytest tests/unit/app/test_renal_dose.py tests/unit/rules/test_interface.py tests/unit/rules/test_engine.py --collect-only -q`
- Collection result: `14 tests collected in 0.02s`.
- Focused test command:
  `python -m pytest tests/unit/app/test_renal_dose.py tests/unit/rules/test_interface.py tests/unit/rules/test_engine.py -q`
- Test result: `14 passed in 0.06s` under Python 3.13.5 and pytest 9.0.2.
- Compile command:
  `python -m compileall -q src/cds/app/renal_dose.py src/cds/rules/interface.py src/cds/rules/engine.py tests/unit/app/test_renal_dose.py tests/unit/rules/test_interface.py tests/unit/rules/test_engine.py`
- Compile result: completed with no output or error.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/app/renal_dose.py` — added the bounded renal-dose application use case and passive app
  result carrying validation beside the standard rule result.
- `tests/unit/app/test_renal_dose.py` — added focused ordered-flow, fail-closed, exact-key,
  unrounded-result, date-consistency, and deferred-exception-mapping tests.
- `src/cds/rules/interface.py` — added the explicit calculated renal result to the minimal rule
  contract.
- `src/cds/rules/engine.py` — passed the explicit calculated renal result to the selected rule and
  preserved it on fail-closed non-match results.
- `tests/unit/rules/test_interface.py` — updated the rule-contract signature tests.
- `tests/unit/rules/test_engine.py` — updated exact-selection and non-match tests to verify explicit
  renal-result propagation.
- `CURRENT.md` — replaced with the Day 61 state and Day 62 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 61 deliverable.
- `AGENTS.md` — source hierarchy, bounded-checkout workflow, implementation boundaries, and close
  procedure.
- `docs/SAFETY_INVARIANTS.md` — validation-before-calculation, exact identifiers, fail-closed behavior,
  repository boundaries, purity, and auditability constraints.
- `CURRENT.md` — authoritative Day 60 state and Day 61 next action.
- `ARCHITECTURE.md` — application-layer orchestration sequence and dependency boundaries.
- `FIRST_VERTICAL_SLICE.md` — stable adult Cockcroft–Gault input, output, and exclusion contract.
- `src/cds/app/context.py` — validated context fields assembled by the use case.
- `src/cds/validation/models.py`, `patient.py`, `lab.py`, `renal.py`, and `medication.py` — existing
  structural and task-sufficiency contracts invoked before calculation and matching.
- `src/cds/repositories/renal_content.py` — exact typed repository key and retrieval contract.
- `src/cds/services/renal.py` — pure unrounded Cockcroft–Gault calculation contract.
- `src/cds/domain/clinical.py`, `enums.py`, `outputs.py`, `support.py`, `value_objects.py`, and
  `exceptions.py` — typed inputs, standard result fields, traceability, and deferred exception types.
- `src/cds/rules/interface.py`, `registry.py`, `engine.py`, `exact_renal_dose.py`, `cefepime.py`, and
  `piperacillin_tazobactam.py` — rule contract, registration, orchestration, and explicit renal-result
  requirements exposed by existing exact medication rules.
- `tests/unit/app/test_context.py`, `tests/unit/rules/test_interface.py`,
  `tests/unit/rules/test_registry.py`, `tests/unit/rules/test_engine.py`,
  `tests/unit/rules/test_cefepime.py`, and `tests/unit/validation/test_medication.py` — existing focused
  conventions and regression expectations.
- `pyproject.toml` — declared pytest configuration and optional development dependencies.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structural and task sufficiency before renal calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed and produce
  no dosing recommendation.
- Medication, rule, regimen, formulation, and content-version identifiers remain exact and
  case-sensitive. Do not trim, normalize, alias, fuzzy-match, infer, or fall back.
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

> Day 62 — map `ContentNotFound`, `CalculationError`, validation-boundary failures, and unexpected
> application or rule exceptions to structured failed results that preserve safe identifiers and
> evaluation time, expose no stack trace or sensitive payload, and remain distinct from expected
> incomplete or unsupported clinical gaps.
