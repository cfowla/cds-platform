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

- Days 1–73 are complete.
- **Day 73 — Extend contract tests** is implemented.
- The next sequential task is **Day 74 — Add content snapshot tests**.

## Current state

- `tests/contract/test_renal_dose_interface_contracts.py` extends contract coverage beyond the
  existing domain-only contracts through the production request mapper, response mapper, and CLI
  interface boundaries.
- Public `__all__` surfaces and defining modules are protected for the renal-dose CLI DTO, typed
  mapped input, request-mapping error, request and response mapper functions, CLI entry points, and
  the five stable CLI exit-code values.
- The configured synthetic use-case fixture returns typed validation, renal, recommendation, dose,
  warning, evidence, provenance, and rule-result objects without introducing clinical logic or
  changing production behavior.
- The canonical CLI response contract protects exact top-level and nested field sets for validation,
  `RuleResult`, `RenalFunctionResult`, `CDSRecommendation`, `DoseRecommendation`, and `Provenance`.
- The contract protects enum wire values, exact Decimal precision and scale, compact deterministic
  JSON, timezone-offset preservation before the application boundary, UTC `Z` serialization,
  provenance timestamps and versions, rule identifiers, order linkage, content versions, evidence,
  and the prototype warning.
- All identifiers and clinical facts in the contract fixture are synthetic. The fixture explicitly
  states that it is not clinical guidance and is not for direct clinical use.
- No production code, clinical content, content review status, renal boundary, supported medication,
  public interface behavior, or serialized contract changed.
- The two Day 72 strict expected-failure cases remain unchanged and continue to document the
  conflicting weight-type and famotidine minimum-weight gaps.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification path was used at `/tmp/cds-platform` for the new contract module only.
- Pytest 9.0.2 was installed in the supplied environment.
- Syntax verification command:
  `python -m py_compile tests/contract/test_renal_dose_interface_contracts.py`
- Syntax verification result: passed.
- A structural line-length check found no lines longer than the configured 100-character limit.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/contract/test_renal_dose_interface_contracts.py --collect-only -q`
- Collection could not begin because the supplied environment did not contain the repository source
  package: `ModuleNotFoundError: No module named 'cds'`.
- Executing the focused contract would require reconstructing the CLI, request and response mapper,
  domain, validation, and serializer import chain. That exceeded the bounded-checkout scope after the
  concrete missing-package error, so verification stopped rather than reconstructing broad source
  directories.
- No focused execution, full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `tests/contract/test_renal_dose_interface_contracts.py` — added end-to-end public import, exit-code,
  canonical response-field, enum, Decimal, UTC datetime, provenance, rule-ID, content-version,
  linkage, evidence, and prototype-warning contract coverage.
- `CURRENT.md` — replaced with the Day 73 state and Day 74 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact Day 73
  and Day 74 roadmap wording.
- `AGENTS.md`, `docs/SAFETY_INVARIANTS.md`, and the prior `CURRENT.md` — bounded execution,
  fail-closed, synthetic-data, auditability, public-contract, and close-procedure requirements.
- `tests/contract/test_domain_serialization_contracts.py` — existing domain-level contract scope that
  Day 73 extends rather than duplicates.
- `src/cds/app/dto.py`, `src/cds/mappers/renal_dose_request.py`,
  `src/cds/mappers/renal_dose_response.py`, and `src/cds/interfaces/cli.py` — current external request,
  mapping, canonical response, public export, and exit-code contracts.
- `tests/unit/mappers/test_renal_dose_response.py` and `tests/unit/interfaces/test_cli.py` — existing
  mapper and CLI conventions and the uncovered end-to-end contract surface.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/outputs.py`,
  `src/cds/domain/support.py`, `src/cds/domain/value_objects.py`,
  `src/cds/validation/models.py`, and `src/cds/utils/serialization.py` — exact typed fields, enum wire
  values, traceability models, validation shape, Decimal behavior, and UTC serialization.
- `src/cds/app/renal_dose.py`, `tests/unit/app/test_renal_dose.py`,
  `tests/integration/test_cefepime_end_to_end.py`, and
  `tests/integration/test_renal_dose_matrix.py` — application output behavior, current full-flow
  assertions, and the Day 72 expected-failure boundaries that must remain unchanged.

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
- Draft content review eligibility remains separate from software contract-test eligibility.
- Conflicting supplied versus declared body-weight type is not currently rejected before calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 74 — add content snapshot tests that make source, version, reviewer, supported-context,
> renal-band, and recommendation changes visible in review without approving draft content or
> changing clinical scope, eligibility, or production behavior.
