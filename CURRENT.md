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

- Days 1–77 are complete.
- **Day 77 — Weekly review: run a safety failure drill** is implemented.
- The next sequential task is **Day 78 — Review the architecture overview**.

## Current state

- `tests/integration/test_safety_failure_drill.py` exercises the existing CLI and application
  failure boundaries as one bounded synthetic safety drill.
- Corrupted JSON is rejected before mapping or application invocation and emits no canonical output.
- An unsupported medication coding system fails closed before content access or rule evaluation and
  produces an incomplete result with no recommendation.
- A corrupted-content repository failure is converted to a structured failed result and the CLI
  content-failure exit path.
- An unexpected rule failure is converted to a structured failed result and the CLI system-failure
  exit path while preserving the existing renal audit result behavior.
- The drill asserts that failed or unsupported paths contain no dosing recommendation and that CLI
  diagnostics expose no traceback, synthetic patient identifier, or injected sensitive payload
  detail.
- The canonical structured response contract was not changed; identifiers already included in that
  contract remain separate from sanitized diagnostic output.
- No clinical calculation, validation behavior, content, recommendation behavior, public interface,
  serialization contract, dependency, or logging configuration changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was created at `/tmp/cds-platform` containing the new focused test
  module.
- Pytest was available in the supplied environment.
- Syntax verification command:
  `python -m py_compile /tmp/cds-platform/tests/integration/test_safety_failure_drill.py`
- Syntax verification result: passed.
- Structural line-length check result: no lines exceeded the configured 100-character limit.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/integration/test_safety_failure_drill.py --collect-only -q`
- Focused collection result: blocked because the supplied environment had no repository checkout and
  the bounded checkout did not contain the imported `cds` package (`ModuleNotFoundError: cds`).
- No focused execution, full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `tests/integration/test_safety_failure_drill.py` — added four collected test cases covering corrupt
  input, unsupported context, corrupted content access, and unexpected rule failure through the CLI
  and application boundaries.
- `CURRENT.md` — replaced with the Day 77 state and Day 78 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact Day 77
  and Day 78 roadmap wording.
- `AGENTS.md`, `docs/SAFETY_INVARIANTS.md`, and the prior `CURRENT.md` — bounded execution, prototype,
  PHI exclusion, fail-closed, verification, and close-procedure requirements.
- `tests/integration/test_renal_safety_invariants.py` — existing integration fixture conventions and
  adjacent Day 75 safety assertions.
- `src/cds/app/renal_dose.py` and `tests/unit/app/test_renal_dose.py` — structured application failure
  mapping, failure stages, and established unit coverage.
- `src/cds/interfaces/cli.py` and `tests/unit/interfaces/test_cli.py` — sanitized CLI diagnostics,
  exit-code mapping, and existing interface-level failure behavior.
- `src/cds/mappers/renal_dose_request.py` and `src/cds/mappers/renal_dose_response.py` — exact request
  wire fields and canonical response serialization used by the integration drill.
- `src/cds/repositories/yaml_renal_content.py` and
  `src/cds/content/renal/cefepime_iv_2_g_every_8_hours_over_30_minutes.yaml` — repository-boundary and
  exact content-field conventions needed to model corrupted content access without changing clinical
  content.

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
- Do not place patient identifiers, clinical payloads, exception messages, or tracebacks in
  diagnostic logs or CLI diagnostics.

## Blockers

- A named independent content reviewer has not been identified.
- Draft content review eligibility remains separate from software contract-test eligibility.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The logging policy is not yet wired into application or interface failure paths.
- Focused Day 77 pytest execution remains unverified in this environment because no complete checkout
  or materialized application import graph was available.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 78 — reconcile `ARCHITECTURE.md` with the implemented modules, dependency direction,
> processing flow, standard result shape, and approved deviations without adding implementation
> history.
