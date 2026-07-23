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

- Days 1–59 are complete.
- **Day 59 — Implement the rule registry** is complete.
- The next sequential task is **Day 60 — Implement the simple engine**.

## Current state

- `src/cds/rules/registry.py` defines immutable `RenalDoseRuleRegistration` values that bind one
  exact medication identifier and one globally unique rule identifier to a `RenalDoseRule`.
- `RenalDoseRuleRegistry` copies supplied registrations into private exact-key storage without
  normalization, aliases, fallback, content loading, calculation, evaluation, logging, or I/O.
- Exact `(medication_id, rule_id)` and globally unique `rule_id` lookups return the registered rule
  or `None` when no exact registration exists.
- One medication may have multiple distinct rules; medication-specific registrations are returned
  as an immutable tuple sorted by rule identifier so behavior is independent of input order.
- Duplicate exact registrations and reused rule identifiers fail during construction with
  `ValueError` before a registry is available.

## Verification

- The execution environment did not supply a repository checkout; the single required
  `git rev-parse --show-toplevel` probe reported that `/mnt/data` is not inside a Git repository.
- No filesystem search, clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the focused registry,
  tests, package initializers, and pytest configuration required for the targeted command.
- Exact command run:
  `python -m pytest tests/unit/rules/test_registry.py`
- Result: `5 passed in 0.03s` under Python 3.13.5 and pytest 9.0.2.
- Optional Ruff verification was not run because Ruff is not installed; it was not installed for
  this task.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/registry.py` — replaced the scaffold with the deterministic exact-identifier rule
  registry and immutable registration model.
- `tests/unit/rules/test_registry.py` — replaced the placeholder with focused exact-lookup,
  deterministic-order, multiple-rule, and duplicate-rejection tests.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 59 deliverable.
- `docs/SAFETY_INVARIANTS.md` — validation-before-matching, fail-closed, purity, exact-content, and
  auditability constraints.
- `CURRENT.md` — authoritative roadmap position, Day 58 rule-interface state, and Day 59 next action.
- `src/cds/rules/interface.py` — exact `RenalDoseRule` protocol stored by the registry.
- `src/cds/repositories/renal_content.py` — existing exact-key, copied-storage, and duplicate-rejection
  conventions used to keep the registry behavior consistent.
- `tests/unit/rules/test_interface.py` — focused synthetic-rule and rules-module test conventions.
- `src/cds/rules/cefepime.py`, `src/cds/rules/piperacillin_tazobactam.py`, and
  `src/cds/rules/exact_renal_dose.py` — current medication identifier and pure rule-evaluation
  boundaries; no changes were required.
- `src/cds/rules/__init__.py` — confirmed no existing compatibility export required modification.
- `pyproject.toml` — targeted pytest configuration and Python support.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before constructing the evaluation context or evaluating
  any registered rule.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed before
  calculation or matching and produce no dosing recommendation.
- Registry identifiers are exact and case-sensitive. Do not trim, normalize, alias, fuzzy-match,
  infer, or fall back to another medication or rule identifier.
- Registration and lookup must not evaluate rules, select or load content, calculate renal function,
  orchestrate workflows, mutate rule implementations, serialize results, log payloads, or perform I/O.
- Rule implementations remain pure and deterministic and return structured `RuleResult` values.
- Draft or retired content is never eligible for rule matching. Software verification does not confer
  clinical review status.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- Clinical-content source interpretations and review eligibility remain separate from this software
  registry task.

## Next exact action

> Day 60 — implement the simple engine that receives validated context and supplied typed content,
> obtains eligible exact registrations from `RenalDoseRuleRegistry`, evaluates them deterministically,
> preserves rule identifiers and content versions, and returns explicit unmatched or unsupported
> structured outcomes without adding validation, content loading, renal calculation, or interface I/O.
