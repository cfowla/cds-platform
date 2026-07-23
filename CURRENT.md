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

- Days 1–60 are complete.
- **Day 60 — Implement the simple engine** is complete.
- The next sequential task is **Day 61 — Create the renal-dose use case**.

## Current state

- `src/cds/rules/engine.py` defines `RenalDoseRuleEngine`, which receives one validated
  `RenalDoseEvaluationContext`, one supplied typed `RenalDoseContent`, and a
  `RenalDoseRuleRegistry` supplied at construction.
- The engine obtains exact case-sensitive medication registrations from the registry and checks
  them in deterministic rule-identifier order.
- Only the registration whose exact `rule_id` matches the supplied content document is evaluated;
  other registrations are not invoked and no normalization, aliases, fallback, or inference occurs.
- Exact matches return the rule implementation's `RuleResult` unchanged, preserving its rule
  identifier, content-version metadata, recommendations, warnings, evidence, provenance, and
  evaluation state.
- A medication identifier with no exact registrations returns an explicit fail-closed
  `NOT_APPLICABLE` result with `outcome_category="unsupported"` and no recommendation.
- Registered medication rules without an exact content-rule match return an explicit fail-closed
  `NOT_APPLICABLE` result with `outcome_category="unmatched"` and no recommendation.
- The engine performs no validation, content loading, version selection, renal calculation,
  exception mapping, serialization, logging, interface work, or I/O.

## Verification

- The execution environment did not supply a repository checkout; the single required
  `git rev-parse --show-toplevel` probe reported that `/mnt/data` is not inside a Git repository.
- No filesystem search, clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the focused engine,
  tests, package initializers, and concretely required typed dependencies.
- Exact command run:
  `python -m pytest tests/unit/rules/test_engine.py`
- Result: `5 passed in 0.07s` under Python 3.13.5 and pytest 9.0.2.
- Optional Ruff verification was attempted with
  `python -m ruff check src/cds/rules/engine.py tests/unit/rules/test_engine.py`, but Ruff is not
  installed; it was not installed for this task.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/engine.py` — replaced the scaffold with deterministic exact-registration rule
  orchestration and explicit unsupported or unmatched outcomes.
- `tests/unit/rules/test_engine.py` — replaced the placeholder with focused exact-selection,
  metadata-preservation, unmatched, unsupported, case-sensitivity, and missing-identifier tests.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 60 deliverable.
- `docs/SAFETY_INVARIANTS.md` — validation-before-matching, fail-closed, exact-content, purity, and
  auditability constraints.
- `ARCHITECTURE.md` — rule-layer responsibility, processing flow, standard-result requirements, and
  application-orchestration boundary.
- `CURRENT.md` — authoritative roadmap position, completed Day 59 registry state, and exact Day 60
  action.
- `src/cds/app/context.py` — validated facts and exact identifiers supplied to the engine.
- `src/cds/domain/enums.py` and `src/cds/domain/outputs.py` — structured `NOT_APPLICABLE` outcomes and
  `RuleResult` audit fields.
- `src/cds/domain/clinical.py`, `src/cds/domain/support.py`, and
  `src/cds/domain/value_objects.py` — typed dependencies required by the focused context and tests.
- `src/cds/repositories/renal_content.py` — typed content identity, rule identifier, content version,
  and supported-context boundary.
- `src/cds/rules/interface.py` and `tests/unit/rules/test_interface.py` — minimal pure rule contract.
- `src/cds/rules/registry.py` and `tests/unit/rules/test_registry.py` — deterministic exact-registration
  ordering and lookup behavior consumed by the engine.
- `src/cds/rules/exact_renal_dose.py` and `src/cds/rules/cefepime.py` — existing rule-result identity,
  content-version, and fail-closed outcome conventions; no changes were required.
- `src/cds/rules/__init__.py` — confirmed no compatibility export required modification.
- `pyproject.toml` — targeted pytest configuration and optional Ruff dependency declaration.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before constructing the evaluation context or invoking the
  engine.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed before
  calculation or matching and produce no dosing recommendation.
- Medication, rule, regimen, and content-version identifiers remain exact and case-sensitive. Do not
  trim, normalize, alias, fuzzy-match, infer, or fall back to another identifier or version.
- Engine orchestration must not validate inputs, load or select content, calculate renal function,
  map exceptions, serialize results, log payloads, or perform I/O.
- Rule implementations remain pure and deterministic and return structured `RuleResult` values.
- Draft or retired content is never eligible for clinical recommendation. Software verification does
  not confer clinical review status.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- Clinical-content source interpretations and review eligibility remain separate from this software
  engine task.

## Next exact action

> Day 61 — create the renal-dose use case that validates structure and sufficiency, loads exact typed
> content, calculates unrounded Cockcroft–Gault creatinine clearance, invokes
> `RenalDoseRuleEngine`, and assembles the standard structured result without moving validation,
> repository parsing, calculation, rule logic, serialization, or interface behavior into the use
> case.
