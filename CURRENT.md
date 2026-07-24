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

- Days 1-79 are complete.
- **Day 79 - Write the clinical-content workflow** is implemented.
- The next sequential task is **Day 80 - Write the validation and missing-data policy**.

## Current state

- `docs/CLINICAL_CONTENT_WORKFLOW.md` defines the controlled renal-dose content lifecycle from scope
  confirmation and source selection through extraction, author checks, independent review,
  eligibility, versioning, supersession, rollback, and verification records.
- The workflow is limited to the chartered first vertical slice and does not expand medications,
  populations, renal methods, settings, regimens, interfaces, or clinical use.
- The document distinguishes the implemented `draft`, `reviewed`, and `retired` schema states from
  the release relationship of supersession.
- Recommendation eligibility remains aligned with the shared matcher: only an exact `reviewed`
  version with complete matching review metadata can proceed to rule matching.
- Exact caller-supplied medication, regimen, and content-version selection remains unchanged. No
  automatic latest-version selection, directory discovery, normalization, fallback, or implicit
  rollback was introduced.
- Reviewed content is treated as immutable; material clinical changes require a new exact content
  version, renewed independent review, and affected verification.
- Rollback selects a previously reviewed exact version and never rewrites reviewed or retired
  history in place.
- A named independent content reviewer remains unidentified, so current content must not be
  represented as independently reviewed based on software checks alone.
- No clinical content, calculation, validation behavior, recommendation behavior, interface,
  serialization contract, dependency, or logging configuration changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was created at `/tmp/cds-platform` containing
  `docs/CLINICAL_CONTENT_WORKFLOW.md` and `CURRENT.md`.
- Documentation structure command:
  `python /tmp/cds-platform/verify_clinical_content_workflow.py`
- Documentation structure result: passed; required lifecycle sections, implemented review states,
  exact-version behavior, fail-closed controls, prototype warning, and 100-character line limit
  were present.
- Pytest was not required because the task changed documentation only and did not change executable
  behavior or a shared software contract.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `docs/CLINICAL_CONTENT_WORKFLOW.md` - added the controlled source, review, versioning,
  supersession, rollback, approval, and independent-verification workflow.
- `CURRENT.md` - replaced with the Day 79 state and Day 80 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` - task structure and exact
  Day 79 and Day 80 roadmap wording.
- `AGENTS.md`, `PROJECT_CHARTER.md`, `FIRST_VERTICAL_SLICE.md`, and
  `docs/SAFETY_INVARIANTS.md` - source hierarchy, scope, clinical-content requirements, safety
  invariants, bounded execution, and close procedure.
- `ARCHITECTURE.md` - documentation style and the implemented content and repository boundaries.
- `src/cds/repositories/renal_content.py`, `src/cds/repositories/renal_content_schema.py`, and
  `src/cds/repositories/yaml_renal_content.py` - exact content types, review states, schema rules,
  source metadata, exact-key retrieval, and file-boundary behavior.
- `src/cds/app/renal_dose.py`, `src/cds/rules/engine.py`, `src/cds/rules/registry.py`,
  `src/cds/rules/cefepime.py`, and `src/cds/rules/exact_renal_dose.py` - explicit version requests,
  exact rule selection, review eligibility, and fail-closed recommendation behavior.

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

> Day 80 - document structural versus sufficiency validation, issue severity, result-state mapping,
> accepted units, missing-data representation, and unsupported-context behavior without changing
> validation or serialized contracts.