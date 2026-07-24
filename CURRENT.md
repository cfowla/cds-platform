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

- Days 1–69 are complete.
- **Day 69 — Add CLI error handling** is complete.
- The next sequential task is **Day 70 — Weekly review: manual CLI walkthrough**.

## Current state

- `src/cds/interfaces/cli.py` retains canonical JSON as the authoritative renal-dose command output.
- The CLI exports stable exit-code constants for success, system failure, input error, unsupported
  request, and content failure.
- `main()` converts unreadable input, malformed JSON, request-mapping failures, structured incomplete
  or not-applicable outcomes, exact-content absence, content-repository failures, failed application
  results, output-write failures, and unexpected interface exceptions into explicit exit behavior.
- Malformed input and unexpected failures produce sanitized stderr diagnostics without stack traces,
  raw exception text, source payloads, patient identifiers, or invented recommendations.
- Structured incomplete, unsupported, content-failure, and system-failure results still preserve the
  canonical JSON response on stdout or at the exact `--output` path before returning nonzero.
- Missing or unsupported units remain validation issues and map to the input-error exit without unit
  inference or conversion.
- Exact absent medication, regimen, and content-version combinations map to the unsupported exit;
  unexpected repository or content-validation failures map to the content-failure exit.
- `--summary` remains presentation-only and isolated from canonical JSON; structured error text is
  appended to stderr without duplicating the prototype warning.
- The interface still does not select or load content, configure repositories or rules, validate
  clinical sufficiency, calculate renal function, match rules, choose recommendations, normalize
  units or identifiers, or add clinical interpretation.
- No clinical scope, supported medication or population, content, calculator, validation, rule,
  use-case, domain-model, mapper, or canonical serialization contract changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the CLI module,
  focused test, existing request and response mapper surfaces, passive DTO and domain dependencies,
  canonical serializer, required package initializers, and `pyproject.toml`.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/interfaces/test_cli.py --collect-only -q`
- Collection result: `14 tests collected in 0.05s`.
- Focused test command:
  `PYTHONPATH=src python -m pytest tests/unit/interfaces/test_cli.py -q`
- Test result: `14 passed in 0.08s`.
- Compile command:
  `python -m compileall -q src/cds/interfaces/cli.py tests/unit/interfaces/test_cli.py`
- Compile result: completed with no output or error.
- Ruff was not installed in the supplied environment, so no lint passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/interfaces/cli.py` — added explicit exit codes, sanitized exception handling, and
  structured-result-to-exit classification while preserving canonical JSON and summary behavior.
- `tests/unit/interfaces/test_cli.py` — added focused malformed-input, mapping, unit, unsupported,
  content-failure, system-failure, no-stack-trace, and nonzero structured-result coverage.
- `CURRENT.md` — replaced with the Day 69 state and Day 70 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and Day 69
  roadmap wording.
- `AGENTS.md` and `docs/SAFETY_INVARIANTS.md` — bounded execution, architecture, prototype warning,
  fail-closed, no-inference, sensitive-data, and verification constraints.
- `src/cds/mappers/renal_dose_request.py` — request-mapping error contract and exact wire conversion.
- `src/cds/mappers/renal_dose_response.py` and `src/cds/utils/serialization.py` — canonical response
  and serialization boundaries used by CLI classification and output.
- `src/cds/app/renal_dose.py`, `src/cds/domain/outputs.py`, and `src/cds/domain/enums.py` — structured
  status, validation, supporting-data, failure-code, and failure-stage contracts.
- `src/cds/domain/exceptions.py`, `src/cds/repositories/renal_content.py`, and
  `tests/unit/app/test_renal_dose.py` — exact-content absence and unexpected repository/system failure
  semantics needed to distinguish unsupported, content, and system exits.
- `src/cds/validation/lab.py` — exact missing and unsupported unit issue codes.
- `src/cds/app/dto.py`, `src/cds/domain/clinical.py`, `src/cds/domain/support.py`, and
  `src/cds/domain/value_objects.py` — direct imports required for focused test collection.
- `pyproject.toml` — Python, pytest, and line-length configuration for focused verification.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers and units exact and case-sensitive; do not normalize, infer, alias, or fall back.
- JSON clinical numerics must remain strings at the request boundary and exact `Decimal` strings at
  the response and summary presentation boundaries; do not convert them through binary floating
  point.
- Missing numerics remain `None`; missing enum categories use explicit `UNKNOWN` members.
- Datetimes crossing mapper and interface boundaries must include a usable UTC offset and serialize
  in UTC; do not assign a timezone to naive input.
- Keep domain models passive, services and rules pure, repositories responsible for content access,
  app modules responsible for orchestration, and mappers and interfaces free of clinical logic.
- Preserve existing public imports and serialized contracts unless a task explicitly changes them.
- Preserve unrounded calculated values for matching and auditability.

## Blockers

- A named independent content reviewer has not been identified.
- Content review eligibility remains separate from this CLI interface task.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 70 — save and verify reproducible synthetic CLI commands and canonical outputs for cefepime,
> piperacillin–tazobactam, and famotidine plus incomplete, unsupported, content-failure, and system-
> failure walkthrough cases without changing clinical logic or content.
