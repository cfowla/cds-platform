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

- Days 1–58 are complete.
- **Day 58 — Implement the minimal rule interface** is complete.
- The next sequential task is **Day 59 — Implement the rule registry**.

## Current state

- `src/cds/rules/interface.py` defines the runtime-checkable `RenalDoseRule` structural protocol.
- The contract exposes only `evaluate(context, content) -> RuleResult` using the validated
  `RenalDoseEvaluationContext` and one supplied typed `RenalDoseContent` document.
- The interface performs no validation, content selection or loading, renal calculation, identifier
  normalization, orchestration, mutation, logging, serialization, interface behavior, or I/O.
- Rule implementations remain responsible for returning structured `RuleResult` values and must be
  pure and deterministic.

## Verification

- The execution environment did not supply a repository checkout; the single required
  `git rev-parse --show-toplevel` probe reported that `/mnt/data` is not inside a Git repository.
- No filesystem search, clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- The new interface and focused tests were reviewed directly against the current application context,
  typed renal content, and `RuleResult` definitions.
- The intended focused command is:
  `python -m pytest tests/unit/rules/test_interface.py`
- Because no checkout was available, the command was not run. If `pytest` is unavailable in a future
  supplied checkout, skip it without installing it and report the limitation.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/interface.py` — added the minimal typed renal-dose rule protocol.
- `tests/unit/rules/test_interface.py` — added focused public-surface, signature, type, and structural
  compatibility tests.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 58 deliverable.
- `docs/SAFETY_INVARIANTS.md` — validation-before-matching, fail-closed, purity, content-boundary, and
  auditability constraints.
- `CURRENT.md` — authoritative roadmap position and active task.
- `src/cds/app/context.py` — exact validated context type required by the interface.
- `src/cds/domain/outputs.py` — structured `RuleResult` return type.
- `src/cds/repositories/renal_content.py` — typed content boundary named by the interface.
- `src/cds/rules/exact_renal_dose.py` and `src/cds/rules/cefepime.py` — current pure rule-evaluation
  conventions and boundaries.
- `src/cds/rules/__init__.py` — confirmed no existing public compatibility export needed modification.
- `tests/unit/app/test_context.py` — focused test conventions and synthetic-data pattern.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before constructing or evaluating the context.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed before
  calculation or matching and produce no dosing recommendation.
- The rule interface must not select or load content, calculate renal function, normalize identifiers,
  infer context, orchestrate workflows, mutate inputs, serialize results, log payloads, or perform I/O.
- Match exact medication, indication, route, formulation, dose, frequency, renal method, renal unit,
  indexing state, stability, renal replacement therapy, and content version without aliases,
  normalization, conversion, inference, interpolation, extrapolation, fallback, or automatic version
  selection.
- Preserve unrounded Decimal renal values and explicit interval ownership.
- Draft or retired content is never eligible for rule matching. Software verification does not confer
  clinical review status.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- Clinical-content source interpretations and review eligibility remain separate from this software
  interface task.

## Next exact action

> Day 59 — implement a deterministic rule registry that maps stable medication and rule identifiers to
> `RenalDoseRule` implementations and rejects duplicate registration without adding engine,
> content-loading, calculation, or interface behavior.
