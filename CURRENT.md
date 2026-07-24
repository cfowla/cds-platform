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

- Days 1–67 are complete.
- **Day 67 — Build the CLI command** is complete.
- The next sequential task is **Day 68 — Add human-readable CLI summary**.

## Current state

- `src/cds/interfaces/cli.py` defines the focused synthetic renal-dose command boundary.
- `run_renal_dose_cli()` reads one UTF-8 JSON input file, delegates parsed-wire validation and typed
  conversion to the existing request mapper, invokes exactly one caller-configured
  `RenalDoseUseCase`, delegates output conversion to the existing canonical response mapper, and
  writes one canonical JSON document with a trailing newline.
- Canonical JSON is written to stdout when no output path is supplied and exclusively to the exact
  optional output path when one is supplied.
- `main()` provides an `argparse` command surface with one required input path and `-o` or `--output`
  for the optional output path.
- The command help preserves the prototype warning and synthetic or properly de-identified data
  requirement.
- Exact identifiers, units, string-derived `Decimal` values, explicit Boolean values, timezone-aware
  datetimes, missing values, validation issues, warnings, evidence, provenance, rule identifiers,
  and content versions remain delegated to the established mapper, application, and serialization
  boundaries without interface normalization or inference.
- `evaluation_date` and `evaluated_at` are required before invocation because the existing use-case
  API requires non-optional typed values; absence raises `RequestMappingError` before the configured
  use case is called.
- The interface does not select or load content, configure repositories or rules, validate clinical
  sufficiency, calculate renal function, match rules, choose recommendations, normalize units or
  identifiers, round values, or add clinical interpretation.
- Human-readable summaries and comprehensive CLI error-to-exit-code handling remain deferred to
  Days 68 and 69 respectively.
- No clinical scope, supported medication or population, content, calculator, validation, rule,
  use-case, domain-model, mapper, or canonical serialization contract changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the CLI module,
  focused test, existing request and response mappers, passive DTO and domain dependencies,
  canonical serializer, required package initializers, and `pyproject.toml`.
- The environment supplied pytest 9.0.2.
- Focused collection command:
  `python -m pytest tests/unit/interfaces/test_cli.py --collect-only -q`
- Collection result: `4 tests collected in 0.02s`.
- Focused test command:
  `python -m pytest tests/unit/interfaces/test_cli.py -q`
- Test result: `4 passed in 0.06s`.
- Compile command:
  `python -m compileall -q src/cds/interfaces/cli.py tests/unit/interfaces/test_cli.py`
- Compile result: completed with no output or error.
- Ruff was not installed in the supplied environment, so no lint passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/interfaces/cli.py` — replaced the scaffold with the dependency-injected renal-dose CLI
  command, canonical stdout or file output, required application-time boundary, and prototype help.
- `tests/unit/interfaces/test_cli.py` — replaced the skipped placeholder with focused command,
  mapping, use-case invocation, stdout, output-path, canonical serialization, and missing-time tests.
- `CURRENT.md` — replaced with the Day 67 state and Day 68 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and Day 67
  roadmap wording.
- `AGENTS.md` — source hierarchy, bounded-checkout rules, architecture boundaries, verification, and
  close procedure.
- `docs/SAFETY_INVARIANTS.md` — prototype, synthetic-data, fail-closed, no-inference, repository, and
  interface safety constraints.
- `src/cds/app/renal_dose.py` — exact configured use-case constructor and evaluation keyword contract.
- `tests/unit/app/test_renal_dose.py` — established configured-use-case test pattern and exact
  invocation fields.
- `src/cds/app/dto.py` and `src/cds/mappers/renal_dose_request.py` — passive request shape, strict JSON
  wire handling, typed mapped inputs, and required CLI application-time responsibility.
- `src/cds/mappers/renal_dose_response.py` and `src/cds/utils/serialization.py` — canonical response
  and deterministic compact JSON boundaries.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/support.py`, and
  `src/cds/domain/value_objects.py` — direct request-mapper dependencies needed for focused test
  collection and execution.
- `src/cds/interfaces/__init__.py`, `src/cds/interfaces/cli.py`, and
  `tests/unit/interfaces/test_cli.py` — package convention and the existing implementation and test
  scaffolds that the task replaced.
- `pyproject.toml` — Python, pytest, and line-length configuration for focused verification.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers and units exact and case-sensitive; do not normalize, infer, alias, or fall back.
- JSON clinical numerics must remain strings at the request boundary and exact `Decimal` strings at
  the response boundary; do not convert them through binary floating point.
- Missing numerics remain `None`; missing enum categories use explicit `UNKNOWN` members.
- Datetimes crossing mapper and interface boundaries must include a usable UTC offset and serialize
  in UTC; do not assign a timezone to naive input.
- Keep domain models passive, services and rules pure, repositories responsible for content access,
  app modules responsible for orchestration, and mappers and interfaces free of clinical logic.
- Preserve existing public imports and serialized contracts unless a task explicitly changes them.
- Preserve unrounded calculated values for matching and auditability.

## Blockers

- A named independent content reviewer has not been identified.
- Content review eligibility remains separate from this CLI command task.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 68 — add an optional human-readable CLI summary that presents concise status, renal result,
> recommendation, warnings, and evidence text while preserving canonical JSON as the authoritative
> machine-readable output and keeping clinical logic outside the interface.
