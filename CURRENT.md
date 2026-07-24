# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:

- repository cloning or broad filesystem searches for another checkout;
- GitHub Actions or CI investigation;
- workflow creation or modification;
- broad repository review; and
- substitute functional test runners.

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1-81 are complete.
- **Day 81 - Create the model and interface reference** is implemented.
- The next sequential task is **Day 82 - Create the prototype release checklist**.

## Current state

- `docs/MODEL_INTERFACE_REFERENCE.md` now documents the implemented domain, validation, and renal
  CLI boundary without changing any model or interface contract.
- The reference distinguishes permissive keyword-only dataclass construction from the stricter
  facts required for a successful renal-dose evaluation.
- Shared value objects, traceability models, clinical truth models, output models, and validation
  result models are documented with current field names, types, safe defaults, and first-slice unit
  requirements.
- Focused import paths and the exact `cds.domain.models` compatibility exports are documented.
- Canonical serialization behavior is documented for dataclasses, enums, `None`, dates, aware
  datetimes, `Decimal`, collections, string-keyed mappings, and unsupported values.
- The flat renal CLI request fields are grouped into required, conditionally required, and optional
  audit-link facts, with exact wire-type and timezone rules.
- The response retains the fixed top-level `validation` and `rule_result` objects and the current
  fail-closed result-state semantics.
- CLI arguments, output streams, exit codes, sanitized diagnostics, dependency injection, and the
  absence of a standalone composition root, console entry point, API, or EHR interface are explicit.
- No Python behavior, model field, enum value, compatibility import, mapper, CLI behavior,
  serialized contract, dependency, clinical content, calculation, validation, or rule behavior
  changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/mnt/data` and did not
  identify a repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was created at `/tmp/cds-platform` containing the new reference,
  updated active-state note, and a task-specific documentation checker.
- Documentation command:
  `python /tmp/cds-platform/verify_model_interface_reference.py`
- Documentation result: passed; required sections, model names, compatibility exports, exact units,
  request and response contracts, CLI limitations, prototype warning, and 100-character line limits
  were present.
- Pytest was not required or run because the task changed documentation only and did not change
  executable behavior or a serialized software contract.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `docs/MODEL_INTERFACE_REFERENCE.md` - added the implemented model, serialization, request,
  response, CLI, compatibility, and limitation reference.
- `CURRENT.md` - replaced with the Day 81 state and Day 82 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` - task structure and exact
  Day 81 and Day 82 roadmap wording.
- `docs/SAFETY_INVARIANTS.md` and `docs/DOMAIN_CONVENTIONS.md` - safety, missing-data, validation,
  unit, traceability, result-state, and serialization policy.
- `src/cds/domain/enums.py`, `support.py`, `value_objects.py`, `clinical.py`, `outputs.py`, and
  `models.py` - exact model fields, defaults, wire values, and compatibility exports.
- `src/cds/validation/models.py`, `patient.py`, `lab.py`, `renal.py`, and `medication.py` -
  validation result shape and actual structural and workflow requiredness.
- `src/cds/app/dto.py` and `src/cds/app/renal_dose.py` - request DTO fields, application result
  shape, identity checks, exact-selection requirements, and result mapping.
- `src/cds/mappers/renal_dose_request.py` and `renal_dose_response.py` - request wire types, mapping
  failures, fixed response keys, and canonical boundary conversion.
- `src/cds/utils/serialization.py` - exact canonical serialization behavior.
- `src/cds/interfaces/cli.py`, `docs/CLI_WALKTHROUGH.md`, `README.md`, and `pyproject.toml` - CLI
  arguments, streams, exit codes, diagnostics, walkthrough behavior, packaging, and limitations.
- `src/cds/domain/__init__.py` and `src/cds/interfaces/__init__.py` - current package-level export
  behavior.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Draft and retired clinical content are not eligible for a dosing recommendation.
- A reviewed status requires complete reviewer metadata for the exact content version.
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
- The current schema has no explicit supersession relationship or automatic active-version registry.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The logging policy is not yet wired into application or interface failure paths.
- Focused Day 77 pytest execution remains unverified in this environment because no complete
  checkout or materialized application import graph was available.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 82 - create a prototype release checklist covering full verification, independent calculation
> review, clinical-content review status, limitations, PHI controls, provenance, version capture,
> and prototype warnings without tagging or changing release eligibility.
