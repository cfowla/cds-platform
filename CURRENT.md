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

- Days 1-82 are complete.
- **Day 82 - Create the prototype release checklist** is implemented.
- The next sequential task is **Day 83 - Tag the prototype milestone**.

## Current state

- `docs/PROTOTYPE_RELEASE_CHECKLIST.md` now defines the evidence and decision record required before
  creating a nonclinical prototype milestone tag.
- The checklist begins with the prototype-only and synthetic or properly de-identified data warning.
- It records the exact candidate commit, package and environment versions, release custodian, and
  verification timestamps.
- Full verification includes the configured pytest, Ruff, and synthetic CLI walkthrough commands,
  with exact result and evidence recording requirements.
- Independent calculation review is separated from software self-test and uses the renal calculator
  specification and existing arithmetic verification record as supporting evidence.
- Clinical-content review is recorded independently for cefepime, piperacillin-tazobactam, and
  famotidine by exact medication, regimen, content, and rule identifiers.
- Draft and retired content remain ineligible, and a missing qualified independent reviewer remains
  a blocking no-go condition.
- The checklist covers fail-closed behavior, PHI and diagnostic controls, provenance, version
  capture, known limitations, and an explicit go or no-go decision.
- Tag creation is explicitly deferred to a separate bounded task and is permitted only after the
  checklist records an explicit go decision for the unchanged candidate commit.
- No Python behavior, test, content document, content review status, release eligibility, version,
  tag, dependency, interface, public contract, or clinical scope changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/mnt/data` and did not
  identify a repository checkout.
- No repository clone, dependency installation, substitute runner, CI, GitHub Actions investigation,
  or tag operation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was created at `/tmp/cds-platform` containing the new checklist,
  updated active-state note, and a task-specific documentation checker.
- Documentation command:
  `python /tmp/cds-platform/verify_prototype_release_checklist.py`
- Documentation result: passed; required safety, verification, calculation-review, content-review,
  PHI-control, provenance, version-capture, limitation, decision, and tagging-handoff sections were
  present, configured commands were exact, prohibited completion claims were absent, and lines did
  not exceed 100 characters.
- Pytest was not required or run because the task changed documentation only and did not change
  executable behavior, clinical content, content eligibility, or a serialized software contract.
- No full-suite, lint, type-check, CI, GitHub Actions, release-readiness, or tag passing claim is
  made.

## Files changed

- `docs/PROTOTYPE_RELEASE_CHECKLIST.md` - added the reusable evidence, no-go, and tagging-handoff
  checklist for one exact nonclinical prototype candidate.
- `CURRENT.md` - replaced with the Day 82 state and Day 83 next action.

## Additional files inspected

- `AGENTS.md`, `docs/TASK_TEMPLATE.md`, and `CDS_12_Week_Daily_Project_Plan.html` - repository
  workflow, task structure, and exact Day 82 and Day 83 roadmap wording.
- `docs/SAFETY_INVARIANTS.md` and `docs/DOMAIN_CONVENTIONS.md` - prototype warning, PHI boundary,
  validation order, fail-closed behavior, units, result states, provenance, and serialization rules.
- `docs/CLINICAL_CONTENT_WORKFLOW.md` - content lifecycle, independent reviewer requirements,
  exact-version eligibility, supersession, rollback, and review-record requirements.
- `docs/RENAL_CALCULATOR_SPEC.md` and `docs/RENAL_CALCULATOR_VERIFICATION.md` - normative equation,
  Decimal and unrounded-value contract, independent arithmetic method, evidence, and limitations.
- `docs/MODEL_INTERFACE_REFERENCE.md` - request and response contracts, CLI behavior, canonical
  serialization, current interface limitations, and reproducible walkthrough command.
- `README.md` and `pyproject.toml` - configured development commands, package version, Python
  support, dependencies, pytest settings, Ruff settings, and prototype warning.
- `src/cds/utils/logging.py` was inspected through its introducing commit because the PHI section
  needed the implemented allowlisted diagnostic boundary and its current wiring limitation.

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
- Do not create a prototype tag unless the release checklist has an explicit go decision for the
  exact unchanged candidate commit and selected content versions.

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
- These blockers prevent an honest release-readiness or tag claim until the checklist records their
  resolution or explicit accepted nonclinical disposition.

## Next exact action

> Day 83 - execute `docs/PROTOTYPE_RELEASE_CHECKLIST.md` in a complete development environment,
> capture the exact software and content versions, update the release record, and create the
> prototype milestone tag only if every required item is complete and the decision is explicitly
> `go`; otherwise stop without tagging and record the blocking evidence.
