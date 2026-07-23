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

- Days 1–52 are complete.
- **Day 52 — Add piperacillin–tazobactam rule coverage** is complete.
- The next sequential task is **Day 53 — Select and source famotidine content**.

## Current state

- `src/cds/rules/exact_renal_dose.py` now provides one pure deterministic exact-regimen matcher for
  typed, validated medication orders, renal results, and reviewed immutable renal-dose content.
- The shared matcher preserves the existing structured result semantics: missing facts are
  incomplete, nonmatching medication is not applicable, unsupported context is warning-bearing and
  fail-closed, and a recommendation is emitted only after one exact reviewed renal band matches.
- Exact matching remains case-sensitive and requires medication, regimen, source-context indication,
  route, formulation, total-product dose, frequency interval, infusion duration, adult population,
  unindexed Cockcroft–Gault method and `mL/min` unit, stable renal function, no renal replacement
  therapy, and the explicitly requested immutable content version.
- The matcher performs no I/O, content selection, identifier normalization, quantity conversion,
  rounding, interpolation, extrapolation, fallback, or clinical-context inference.
- `src/cds/rules/piperacillin_tazobactam.py` is a thin medication configuration and public evaluation
  wrapper; it adds no medication-specific engine branches.
- Focused synthetic tests cover the selected standard-infusion 3.375 g regimen, standard-infusion
  4.5 g nosocomial-pneumonia source context, and extended-infusion 3.375 g regimen, including the
  exact null formulation for the extended-infusion document.
- Focused tests also lock unrounded `20` and `40 mL/min` boundary ownership, total combined-product
  gram units, missing facts, unsupported exact context, patient identity, review eligibility, and
  immutable content-version behavior.
- The three source-based piperacillin–tazobactam documents remain `draft` and therefore cannot produce
  a successful recommendation until independent clinical-content review is completed.
- Cefepime behavior, public imports, repository interfaces, serialized contracts, medication scope,
  population scope, and clinical content were not changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` failed because no repository
  checkout was present; no filesystem search or clone was attempted.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the focused rule files,
  focused tests, and only imports required by test collection.
- `pytest` was available in the environment; no dependency was installed.
- Focused collection completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_piperacillin_tazobactam.py --collect-only -q`.
- Result: `30 tests collected in 0.05s`.
- Focused execution completed successfully:
  `PYTHONPATH=src python -m pytest tests/unit/rules/test_piperacillin_tazobactam.py -q`.
- Result: `30 passed in 0.11s`.
- `python -m compileall -q src/cds/rules/exact_renal_dose.py src/cds/rules/piperacillin_tazobactam.py tests/unit/rules/test_piperacillin_tazobactam.py`
  completed successfully.
- The committed GitHub blobs were compared with the verified local files and matched exactly.
- The full suite was not run because no complete checkout was available and the existing cefepime
  rule was not migrated to the new shared matcher in this bounded task.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/rules/exact_renal_dose.py` — created.
- `src/cds/rules/piperacillin_tazobactam.py` — created.
- `tests/unit/rules/test_piperacillin_tazobactam.py` — created.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `AGENTS.md` — source hierarchy, bounded-checkout rules, rule-layer boundary, verification, and close
  procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task-template structure and the
  exact Day 52 deliverable.
- `docs/SAFETY_INVARIANTS.md` — fail-closed matching, explicit units and context, review eligibility,
  purity, and auditability constraints.
- `src/cds/rules/cefepime.py` and `tests/unit/rules/test_cefepime.py` — current exact-regimen result
  semantics and focused rule-test contract used to extract only demonstrated shared behavior.
- `src/cds/rules/predicates.py` — imported unrounded renal-band predicate.
- `src/cds/repositories/renal_content.py` — typed content contract imported by the new matcher and
  wrapper.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/outputs.py`,
  `src/cds/domain/support.py`, and `src/cds/domain/value_objects.py` — direct typed imports required by
  focused test collection and execution.
- The three Day 51 piperacillin–tazobactam YAML documents — exact medication, regimen, indication,
  formulation, quantity, infusion, renal boundary, version, and draft-review identifiers exercised
  by the focused tests.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed without a
  dosing recommendation.
- Match exact medication, regimen, indication, route, formulation, total-product dose, frequency,
  infusion duration, renal method, renal unit, indexing state, stability, renal replacement therapy,
  and content version without aliases, normalization, fuzzy matching, conversion, inference,
  interpolation, extrapolation, fallback, or automatic version selection.
- Rule evaluators remain pure and deterministic; content is supplied as typed data through the
  repository boundary.
- Draft or retired content is never eligible for rule matching. Software verification does not
  confer clinical review status.
- Preserve unrounded Decimal renal values, explicit units, result categories, warnings, evidence,
  provenance, rule identifiers, implementation versions, and content versions.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- All three piperacillin–tazobactam documents remain draft and cannot produce a successful
  recommendation in non-synthetic use until their recorded source, boundary, formulation, evidence,
  monitoring, and total-product-dose decisions are independently reviewed.

## Next exact action

> Day 53 — select and source famotidine content by defining exact medication and regimen identifiers,
> authoritative source and version, supported routes and regimens, renal thresholds, limitations,
> and required reviewer metadata without yet encoding content or implementing a rule.
