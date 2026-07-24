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

- Days 1–68 are complete.
- **Day 68 — Add human-readable CLI summary** is complete.
- The next sequential task is **Day 69 — Add CLI error handling**.

## Current state

- `src/cds/interfaces/cli.py` retains canonical JSON as the authoritative renal-dose command output.
- `main()` adds an optional `--summary` flag.
- When requested, the human-readable summary is written only to stderr or the caller-supplied
  summary stream; canonical JSON remains isolated on stdout or at the exact `--output` path.
- The summary preserves the prototype warning and synthetic or properly de-identified data
  requirement.
- The summary presents the existing structured result status, exact unrounded renal value and unit,
  recommendation text, warning text, and evidence text without calculation, rounding, normalization,
  fallback selection, or clinical inference.
- Missing renal or recommendation data is described as absent from the structured result rather than
  replaced with an invented value or recommendation.
- Warning and evidence text is selected from the existing canonical validation, rule-result, renal,
  recommendation, and dose-recommendation structures; duplicate text is suppressed only for display.
- The interface still does not select or load content, configure repositories or rules, validate
  clinical sufficiency, calculate renal function, match rules, choose recommendations, normalize
  units or identifiers, or add clinical interpretation.
- Comprehensive CLI error-to-exit-code handling remains deferred to Day 69.
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
- The environment supplied pytest 9.0.2.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/interfaces/test_cli.py --collect-only -q`
- Collection result: `6 tests collected in 0.02s`.
- Focused test command:
  `PYTHONPATH=src python -m pytest tests/unit/interfaces/test_cli.py -q`
- Test result: `6 passed in 0.04s`.
- Compile command:
  `python -m compileall -q src/cds/interfaces/cli.py tests/unit/interfaces/test_cli.py`
- Compile result: completed with no output or error.
- Ruff was not installed in the supplied environment, so no lint passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/interfaces/cli.py` — added optional presentation-only summary output on a separate stream
  while preserving canonical JSON output behavior.
- `tests/unit/interfaces/test_cli.py` — added focused summary, exact Decimal text, prototype warning,
  structured-field presentation, missing-result handling, and JSON-stream-separation coverage.
- `CURRENT.md` — replaced with the Day 68 state and Day 69 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and Day 68
  roadmap wording.
- `AGENTS.md` — source hierarchy, bounded-checkout rules, architecture boundaries, verification, and
  close procedure.
- `PROJECT_CHARTER.md` and `docs/SAFETY_INVARIANTS.md` — user-facing prototype warning,
  synthetic-data, traceability, no-inference, and fail-closed constraints.
- `src/cds/app/renal_dose.py` — exact use-case result structure and application responsibilities.
- `src/cds/app/dto.py` and `src/cds/mappers/renal_dose_request.py` — existing CLI request and mapping
  boundaries required by focused test collection and execution.
- `src/cds/mappers/renal_dose_response.py` and `src/cds/utils/serialization.py` — canonical response
  mapping, exact Decimal strings, deterministic JSON, and presentation input shape.
- `src/cds/domain/outputs.py`, `src/cds/domain/support.py`, and
  `src/cds/domain/value_objects.py` — renal, recommendation, warning, evidence, and unit-bearing field
  names used by the summary presentation.
- `src/cds/domain/clinical.py` and `src/cds/domain/enums.py` — direct request-mapper dependencies
  required for focused test collection and execution.
- `src/cds/interfaces/__init__.py`, `src/cds/interfaces/cli.py`, and
  `tests/unit/interfaces/test_cli.py` — package convention and focused implementation and tests.
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
- Content review eligibility remains separate from this CLI presentation task.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 69 — add focused CLI error handling that maps malformed input, unsupported medication or
> regimen, ambiguous units, content failure, and system failure to explicit exit behavior without
> stack traces, sensitive payload disclosure, or invented recommendations.
