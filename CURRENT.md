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

- Days 1–64 are complete.
- **Day 64 — Define the CLI request DTO** is complete.
- The next sequential task is **Day 65 — Implement request mapping**.

## Current state

- `src/cds/app/dto.py` defines the passive, frozen, slotted, keyword-only
  `RenalDoseCLIRequest` data-transfer object.
- The DTO specifies the minimal synthetic renal-dose CLI wire facts for patient identity and birth
  date, sex, supplied weight and type, serum-creatinine value and collection facts, explicit renal
  stability and exclusion facts, exact medication and regimen identifiers, regimen-specific route,
  dose, frequency, indication, and infusion facts, requested content version, evaluation date, and
  timezone-bearing evaluation time.
- Date, datetime, Decimal, enum, unit, and identifier values remain in their JSON wire
  representation. Day 64 adds no parsing or conversion behavior; the Day 65 mapper owns those
  decisions.
- Every field defaults to `None`, preserving missing source data without fabricating a numeric,
  categorical, temporal, identifier, unit, or Boolean value.
- The DTO performs no validation, normalization, inference, domain construction, serialization,
  calculation, content loading, rule matching, I/O, or mutation.
- No clinical scope, supported medication or population, content, calculator, validation, rule,
  use-case, serialization, mapper, interface, or public domain contract changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with only the new DTO,
  focused test, package initializers, and `pyproject.toml` needed for pytest configuration.
- The environment supplied pytest 9.0.2.
- Focused collection command:
  `python -m pytest tests/unit/app/test_dto.py --collect-only -q`
- Collection result: `4 tests collected in 0.01s`.
- Focused test command:
  `python -m pytest tests/unit/app/test_dto.py -q`
- Test result: `4 passed in 0.05s`.
- Compile command:
  `python -m compileall -q src/cds/app/dto.py tests/unit/app/test_dto.py`
- Compile result: completed with no output or error.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/app/dto.py` — added the passive synthetic renal-dose CLI request DTO.
- `tests/unit/app/test_dto.py` — added focused field-shape, wire-preservation, missing-data, and
  passivity tests.
- `CURRENT.md` — replaced with the Day 64 state and Day 65 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and Day 64
  roadmap wording.
- `AGENTS.md` — source hierarchy, bounded-checkout rules, architecture boundaries, and close
  procedure.
- `docs/SAFETY_INVARIANTS.md` — missing-data, explicit-unit, no-inference, and fail-closed
  constraints.
- `ARCHITECTURE.md` — DTO, mapper, application, and interface responsibility boundaries.
- `docs/RENAL_CALCULATOR_SPEC.md` — authoritative birth-date plus evaluation-date age input,
  explicit time, exact units, and Decimal requirements.
- `src/cds/app/renal_dose.py` — current use-case input facts and exact identifier requirements.
- `src/cds/rules/context.py` — validated context fields that the future mapper must support.
- `src/cds/domain/enums.py` and `src/cds/domain/clinical.py` — target enum and domain-object fields
  for the future mapping boundary.
- `src/cds/validation/lab.py` and `src/cds/validation/medication.py` — exact laboratory and regimen
  facts required for successful downstream validation.
- `tests/unit/app/test_context.py` — existing passive application-data-object test conventions.
- `src/cds/__init__.py`, `src/cds/app/__init__.py`, and `pyproject.toml` — bounded package and pytest
  configuration requirements.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers and units exact and case-sensitive; do not normalize, infer, alias, or fall back.
- JSON clinical numerics must not be converted through binary `float`; the future mapper must create
  `Decimal` values explicitly from supported wire strings.
- Keep domain models passive, services and rules pure, repositories responsible for content access,
  app modules responsible for orchestration, and mappers and interfaces free of clinical logic.
- Preserve existing public imports and serialized contracts unless a task explicitly changes them.
- Preserve unrounded calculated values for matching and auditability.

## Blockers

- A named independent content reviewer has not been identified.
- Content review eligibility remains separate from this request-contract task.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 65 — implement a focused request mapper that converts parsed synthetic JSON into
> `RenalDoseCLIRequest` and then into the existing typed patient, serum-creatinine, medication-order,
> enum, value-object, date, and timezone-aware datetime inputs with explicit missing-data, Decimal,
> unit, and exact-identifier handling and no clinical decision logic.
