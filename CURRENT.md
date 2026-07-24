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

- Days 1–78 are complete.
- **Day 78 — Review the architecture overview** is implemented.
- The next sequential task is **Day 79 — Write the clinical-content workflow**.

## Current state

- `ARCHITECTURE.md` now describes the implemented package map and the executable dependency
  allowlist enforced by `tests/contract/test_architecture_boundaries.py`.
- The dependency section distinguishes the practical inward flow from the exact
  layer-to-layer import permissions used by the current prototype.
- The processing flow now follows the implemented CLI request DTO, request mapper, structural and
  sufficiency validation, exact repository lookup, context assembly, pure renal calculation, rule
  engine, application result wrapper, response mapper, canonical serializer, and presentation-only
  summary.
- The standard result shape is documented as `RenalDoseUseCaseResult` with top-level
  `validation` and `rule_result` objects, exact result statuses, tri-state fields, audit links, and
  canonical JSON behavior.
- Current prototype placements are explicit: typed content models live at the repository boundary,
  the canonical evaluation context lives in `rules.context`, and `app.context` is a compatibility
  export. The CLI DTO lives in `app.dto`, and the CLI remains dependency injected.
- The architecture overview contains no implementation diary, feature history, clinical-content
  expansion, public-contract change, or new abstraction.
- No clinical calculation, validation behavior, content, recommendation behavior, interface,
  serialization contract, dependency, or logging configuration changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was created at `/tmp/cds-platform` containing `ARCHITECTURE.md`,
  `CURRENT.md`, and the focused architecture contract test.
- Pytest was available in the supplied environment.
- Documentation structure command:
  `python /tmp/cds-platform/verify_architecture_doc.py`
- Documentation structure result: passed; required sections, implemented result keys, approved
  deviations, prototype warning, and 100-character line-length limit were present.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/contract/test_architecture_boundaries.py --collect-only -q`
- Focused collection result: 3 tests collected.
- Focused execution was not run because the bounded checkout intentionally did not reconstruct the
  full `src/cds` package required by the contract test.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `ARCHITECTURE.md` — reconciled stable boundaries with implemented modules, dependency permissions,
  processing flow, result shape, and approved prototype deviations.
- `CURRENT.md` — replaced with the Day 78 state and Day 79 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact
  Day 78 and Day 79 roadmap wording.
- `AGENTS.md`, `docs/SAFETY_INVARIANTS.md`, and the prior `CURRENT.md` — source hierarchy, bounded
  execution, safety constraints, verification rules, and close procedure.
- `tests/contract/test_architecture_boundaries.py` — executable layer allowlist and pure-layer I/O
  restrictions that the architecture overview must describe.
- `src/cds/app/dto.py`, `src/cds/app/context.py`, and `src/cds/app/renal_dose.py` — request DTO,
  compatibility context export, orchestration order, result wrapper, and structured failure mapping.
- `src/cds/domain/enums.py`, `src/cds/domain/outputs.py`, and `src/cds/validation/models.py` — exact
  status values, standard result fields, and validation result shape.
- `src/cds/services/renal.py`, `src/cds/rules/context.py`, and `src/cds/rules/engine.py` — pure
  calculation boundary, canonical evaluation context, and deterministic exact-rule evaluation.
- `src/cds/repositories/renal_content.py` and `src/cds/repositories/yaml_renal_content.py` — typed
  content ownership, exact-key repository contract, file boundary, schema conversion, and lookup
  behavior.
- `src/cds/mappers/renal_dose_request.py`, `src/cds/mappers/renal_dose_response.py`,
  `src/cds/interfaces/cli.py`, and `src/cds/utils/serialization.py` — external mapping, top-level
  response keys, CLI responsibilities, and canonical serialization behavior.

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
- Focused Day 77 pytest execution remains unverified in this environment because no complete
  checkout or materialized application import graph was available.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 79 — document clinical-content source selection, extraction, review, versioning, approval
> status, supersession, rollback, and independent verification without changing content eligibility
> or clinical scope.
