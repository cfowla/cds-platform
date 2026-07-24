# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:
- repository cloning or broad filesystem searches for another checkout
- GitHub Actions or CI investigation
- workflow creation or modification
- broad repository review
- substitute functional test runners

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–72 are complete.
- **Day 72 — Add full-flow parameterized tests** is implemented.
- The next sequential task is **Day 73 — Extend contract tests**.

## Current state

- `tests/integration/test_renal_dose_matrix.py` implements the Day 72 full-flow matrix through the
  production `RenalDoseUseCase` boundary.
- Six exact regimen variants are represented: two cefepime, three piperacillin–tazobactam, and one
  famotidine regimen.
- Thirteen renal-threshold families expand to 39 stable-ID cases immediately below, exactly at, and
  immediately above each boundary using unrounded Cockcroft–Gault `Decimal` values.
- Successful cases assert exact content lookup, one calculation, one engine invocation, exact band
  selection, structured dose fields, rule and content versions, evidence, provenance, order linkage,
  and canonical Decimal and UTC serialization.
- Initial-validation cases prove repository, calculator, and rule-engine stop behavior for missing,
  mismatched, unsupported, or insufficient patient, laboratory, medication, and context facts.
- Content-specific missing-order cases prove exact repository lookup occurs before calculation and
  rule evaluation stop.
- Unsupported exact-context cases cover medication, casing, regimen, version, route, formulation,
  dose, interval, infusion, indication, pediatric scope, renal replacement therapy, and unstable
  renal function without normalization, conversion, inference, or fallback.
- Structured failure cases cover typed validation, missing and unexpected content, context assembly,
  typed and unexpected calculation, and unexpected rule failures without exposing exception text.
- Draft YAML remains ineligible. The suite copies each document into an explicitly labeled test-only
  reviewed in-memory fixture without altering or clinically approving repository content.
- Two strict expected-failure tests document existing behavior gaps: conflicting supplied versus
  declared weight type is not rejected, and the famotidine adult minimum-weight boundary is not
  enforced. Neither gap was hidden by changing the test expectation or expanding production scope.
- No production code, clinical content, content review status, renal boundary, supported medication,
  public interface, or serialized contract changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification path was used at `/tmp/cds-platform` for the new test module only.
- Syntax verification command:
  `python -m py_compile tests/integration/test_renal_dose_matrix.py`
- Syntax verification result: passed.
- Line-length structural check found no lines longer than the configured 100-character limit.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/integration/test_renal_dose_matrix.py --collect-only -q`
- Pytest was installed, but collection could not complete because the supplied environment did not
  contain the repository source package: `ModuleNotFoundError: No module named 'cds.app.renal_dose'`.
- No focused execution, full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `tests/integration/test_renal_dose_matrix.py` — added the six-regimen full-flow harness, 39 renal
  boundary cases, validation and exact-context partitions, structured failure injection, draft
  ineligibility coverage, and reusable fail-closed assertions.
- `CURRENT.md` — replaced with the Day 72 state and Day 73 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact Day 72
  and Day 73 roadmap wording.
- `AGENTS.md`, `docs/SAFETY_INVARIANTS.md`, and `docs/INTEGRATION_TEST_MATRIX.md` — bounded execution,
  prototype, exact-input, fail-closed, auditability, and matrix acceptance criteria.
- `src/cds/app/renal_dose.py` and `tests/unit/app/test_renal_dose.py` — orchestration order,
  validation stop points, exact repository lookup, and structured failure mappings.
- `tests/integration/test_cefepime_end_to_end.py` — existing reviewed-test-copy and canonical-output
  integration convention.
- The renal rule engine, registry, shared exact matcher, and cefepime, piperacillin–tazobactam, and
  famotidine rule adapters — production full-flow registration and evaluation contracts.
- Patient, laboratory, and renal validators — exact issue codes and pre-calculation stop behavior.
- The six current renal-content YAML files — exact identifiers, formulations, source contexts,
  review status, renal bands, and threshold inclusivity.
- `src/cds/utils/serialization.py` was referenced through the established canonical serializer used
  by the focused integration assertion.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Draft clinical content is not eligible for production rule matching and has not received
  independent clinical-content review.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers and units exact and case-sensitive; do not normalize, infer, alias, convert, or
  fall back.
- JSON clinical numerics remain strings at request boundaries and exact Decimal strings at response
  boundaries; do not convert them through binary floating point.
- Missing numerics remain `None`; missing enum categories use explicit `UNKNOWN` members.
- Datetimes crossing mapper and interface boundaries must include a usable UTC offset and serialize
  in UTC; do not assign a timezone to naive input.
- Keep domain models passive, services and rules pure, repositories responsible for content access,
  app modules responsible for orchestration, and mappers and interfaces free of clinical logic.
- Preserve existing public imports and serialized contracts unless a task explicitly changes them.
- Preserve unrounded calculated values for matching and auditability.

## Blockers

- A named independent content reviewer has not been identified.
- Draft content review eligibility remains separate from software integration-test eligibility.
- Conflicting supplied versus declared body-weight type is not currently rejected before calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 73 — extend contract tests to protect end-to-end output fields, enum wire values, Decimal
> formatting, UTC datetime behavior, provenance, rule IDs, content versions, and compatibility
> imports beyond the existing domain-level contracts. Preserve the two Day 72 strict expected-failure
> cases until separately bounded fixes enforce their documented safety boundaries.
