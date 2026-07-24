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

- Days 1–65 are complete.
- **Day 65 — Implement request mapping** is complete.
- The next sequential task is **Day 66 — Implement response mapping**.

## Current state

- `src/cds/mappers/renal_dose_request.py` defines the focused synthetic renal-dose request mapping
  boundary.
- `dto_from_mapping()` accepts one parsed JSON object, rejects unknown fields and incorrect JSON
  primitive types, preserves exact string and Boolean wire values, and never converts a JSON number
  through binary `float` for a clinical numeric.
- `map_renal_dose_request()` converts `RenalDoseCLIRequest` into a frozen
  `RenalDoseMappedInput` containing the existing typed `Patient`, serum-creatinine `LabResult`,
  `MedicationOrder`, `Sex`, `WeightType`, `ValueWithUnit`, `CodeableConcept`, date, and timezone-aware
  datetime inputs.
- Clinical numerics are constructed directly from source strings as `Decimal`; supplied precision,
  identifiers, units, casing, and timezone offsets remain visible.
- Missing numeric, identifier, unit, temporal, and Boolean values remain `None` where permitted.
  Missing controlled categories map to their explicit `UNKNOWN` enum members rather than fabricated
  values.
- Malformed Decimal, ISO date, ISO datetime, naive datetime, unsupported enum, unknown-field, and
  wrong-wire-type inputs raise `RequestMappingError` before application use-case invocation.
- The mapper performs no clinical validation, unit conversion, normalization, identifier lookup,
  calculation, content access, rule matching, recommendation selection, serialization, or I/O.
- Clinically invalid but representable values remain available for the existing validation layer to
  reject; the mapper does not make insufficient input sufficient.
- No clinical scope, supported medication or population, content, calculator, validation, rule,
  use-case, serialization, interface, or public domain contract changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the mapper, focused
  test, DTO, directly imported domain modules, required package initializers, and `pyproject.toml`.
- The environment supplied pytest 9.0.2.
- Focused collection command:
  `python -m pytest tests/unit/mappers/test_renal_dose_request.py --collect-only -q`
- Collection result: `14 tests collected in 0.08s`.
- Focused test command:
  `python -m pytest tests/unit/mappers/test_renal_dose_request.py -q`
- Test result: `14 passed in 0.07s`.
- Compile command:
  `python -m compileall -q src/cds/mappers/renal_dose_request.py tests/unit/mappers/test_renal_dose_request.py`
- Compile result: completed with no output or error.
- Ruff was not installed in the supplied environment, so no lint passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/mappers/renal_dose_request.py` — added the parsed-JSON-to-DTO and DTO-to-typed-input
  mapping boundary.
- `tests/unit/mappers/test_renal_dose_request.py` — added focused wire-shape, exact-conversion,
  missing-data, invalid-representation, strict-enum, timezone, and validation-boundary tests.
- `CURRENT.md` — replaced with the Day 65 state and Day 66 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and Day 65
  roadmap wording.
- `AGENTS.md` — source hierarchy, bounded-checkout rules, architecture boundaries, and close
  procedure.
- `docs/SAFETY_INVARIANTS.md` and `docs/DOMAIN_CONVENTIONS.md` — missing-data, explicit-unit,
  exact-enum, Decimal, timezone, and no-inference conventions.
- `ARCHITECTURE.md` — mapper, application, validation, domain, and interface responsibility
  boundaries.
- `src/cds/app/dto.py` and `src/cds/app/renal_dose.py` — source wire contract and target use-case
  inputs.
- `src/cds/rules/context.py` — validated renal-dose facts that later orchestration must preserve.
- `src/cds/domain/enums.py`, `src/cds/domain/clinical.py`, `src/cds/domain/value_objects.py`, and
  `src/cds/domain/support.py` — exact target enums, domain models, nested values, and import chain.
- `src/cds/services/renal.py` — direct confirmation that clinical quantities require string-derived
  `Decimal`, exact units, explicit weight type, and timezone-aware calculation time.
- `src/cds/validation/patient.py`, `src/cds/validation/lab.py`, and
  `src/cds/validation/medication.py` — confirmation that clinical sufficiency and supported-value
  decisions remain downstream of mapping.
- `tests/unit/app/test_dto.py` — existing request-wire fixtures and passive DTO conventions.
- `src/cds/__init__.py`, `src/cds/app/__init__.py`, `src/cds/domain/__init__.py`,
  `src/cds/mappers/__init__.py`, and `pyproject.toml` — bounded package and pytest configuration.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers and units exact and case-sensitive; do not normalize, infer, alias, or fall back.
- JSON clinical numerics must be strings at the request boundary and become `Decimal` without binary
  floating-point conversion.
- Missing numerics remain `None`; missing enum categories use explicit `UNKNOWN` members.
- Datetimes crossing the mapper boundary must include a usable UTC offset; do not assign a timezone
  to naive input.
- Keep domain models passive, services and rules pure, repositories responsible for content access,
  app modules responsible for orchestration, and mappers and interfaces free of clinical logic.
- Preserve existing public imports and serialized contracts unless a task explicitly changes them.
- Preserve unrounded calculated values for matching and auditability.

## Blockers

- A named independent content reviewer has not been identified.
- Content review eligibility remains separate from this input-mapping task.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 66 — implement a focused response mapper that converts the existing renal-dose use-case result
> into stable canonical JSON-compatible output with ISO dates, UTC datetimes, Decimal strings,
> structured validation issues, warnings, evidence, provenance, rule identifiers, and content
> versions, without adding clinical logic or changing the standard result contract.
