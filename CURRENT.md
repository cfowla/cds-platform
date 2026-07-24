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

- Days 1–76 are complete.
- **Day 76 — Add logging policy** is implemented.
- The next sequential task is **Day 77 — Weekly review: run a safety failure drill**.

## Current state

- `src/cds/utils/logging.py` defines a standard-library diagnostic logging boundary with a fixed,
  allowlisted field set rather than arbitrary metadata.
- Diagnostic values must be lower-case controlled tokens; free text, JSON-like payloads, whitespace,
  and mixed-case failure codes are rejected before a log record is emitted.
- `log_diagnostic` accepts only event, component, operation, stage, status, and failure-code fields;
  it has no patient-identifier, clinical-value, request-payload, response-payload, or arbitrary-extra
  parameter.
- `log_failure` records the exception class only. It does not emit the exception message, arguments,
  payload details, traceback, or `exc_info`.
- Log records expose the same allowlisted values under `cds_*` structured fields for formatters and
  handlers without carrying sensitive case data.
- Focused tests use synthetic identifiers and payload details to prove that failure output does not
  disclose them and that payload-like diagnostic values are rejected.
- No clinical calculation, validation behavior, content, recommendation behavior, public interface,
  serialized contract, dependency, or logging backend configuration changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was used at `/tmp/cds-platform` for the new utility and focused
  test module.
- Pytest was available in the supplied environment.
- Syntax verification command:
  `python -m py_compile src/cds/utils/logging.py tests/unit/utils/test_logging.py`
- Syntax verification result: passed.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/utils/test_logging.py --collect-only -q`
- Focused collection result: 7 tests collected.
- Focused execution command:
  `PYTHONPATH=src python -m pytest tests/unit/utils/test_logging.py -q`
- Focused execution result: 7 passed in 0.03 seconds.
- A structural line-length check found no lines longer than the configured 100-character limit.
- Ruff was not installed in the supplied environment, so no Ruff passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/utils/logging.py` — added the allowlisted, privacy-preserving diagnostic and failure
  logging helpers.
- `tests/unit/utils/test_logging.py` — added seven tests for safe fields, payload rejection, exception
  sanitization, and absence of patient or payload parameters.
- `CURRENT.md` — replaced with the Day 76 state and Day 77 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact Day 76
  and Day 77 roadmap wording.
- `AGENTS.md`, `docs/SAFETY_INVARIANTS.md`, and the prior `CURRENT.md` — bounded execution, prototype,
  PHI exclusion, scope, verification, and close-procedure requirements.
- `src/cds/interfaces/cli.py` and `tests/unit/interfaces/test_cli.py` — existing sanitized diagnostic
  behavior and exception-detail suppression at the current user-facing interface boundary.
- `src/cds/utils/__init__.py` and `pyproject.toml` — package convention, Python version, pytest
  configuration, and configured line-length limit.

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
  diagnostic logs.

## Blockers

- A named independent content reviewer has not been identified.
- Draft content review eligibility remains separate from software contract-test eligibility.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The new logging policy is not yet wired into application or interface failure paths.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 77 — run a bounded safety failure drill that corrupts content and input, exercises unsupported
> contexts and system errors, and proves fail-closed results contain no recommendation, exposed
> stack trace, patient identifier, or sensitive synthetic payload detail.
