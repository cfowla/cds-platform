# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available, use
the GitHub connector to materialize only named files and concretely required imports in a bounded
verification checkout.

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
- **Day 83 - Tag the prototype milestone** was attempted against candidate commit
  `ffbe2e507df76d23425371755945aa9c442a0300`.
- Day 83 is not complete because the prototype release checklist does not record an explicit `go`.
- No changelog, release tag, release metadata, clinical content, code, tests, or public contract
  changed.

## Current state

- Package version `0.1.0` was confirmed from `pyproject.toml`.
- The release checklist remains an unexecuted template with unchecked required items and placeholder
  candidate, reviewer, evidence, content-version, limitation-disposition, and decision fields.
- Independent calculation approval is not recorded for the exact candidate.
- Independent clinical-content review is not recorded for every selected exact content version.
- A named qualified independent content reviewer remains unavailable.
- The exact full-suite, Ruff, and CLI walkthrough evidence required by the checklist is not
  available.
- The release decision is therefore `no-go`.
- The checklist requires an explicit `go` before a changelog or release record is updated and before
  a prototype milestone tag is created.
- No tag operation was attempted.

## Verification

- `git rev-parse --show-toplevel` was run once from `/mnt/data`; no repository checkout was present.
- No repository clone, broad filesystem search, dependency installation, CI investigation, or
  GitHub Actions investigation was attempted.
- `python --version` reported `Python 3.13.5`.
- `python -m pytest --version` reported `pytest 9.0.2`.
- The full pytest suite was not run because no complete repository checkout was available.
- `python -m ruff --version` failed because Ruff is not installed in the supplied environment.
- Ruff was not installed because the repository instructions prohibit installing missing
  dependencies in this constrained environment.
- The synthetic CLI walkthrough was not run because the complete repository and import graph were
  unavailable.
- No full-suite, lint, CLI, release-readiness, checklist-completion, or tag passing claim is made.

## Files changed

- `CURRENT.md` - replaced with the Day 83 no-go outcome, exact attempted candidate, verification
  limitations, and the next release-gate action.

## Additional files inspected

- `AGENTS.md` - repository execution, bounded-checkout, verification, and close procedures.
- `docs/TASK_TEMPLATE.md` - bounded task structure and release-task close requirements.
- `CDS_12_Week_Daily_Project_Plan.html` - exact Day 83 roadmap wording.
- `docs/SAFETY_INVARIANTS.md` - prototype warning, PHI boundary, and fail-closed constraints.
- `docs/PROTOTYPE_RELEASE_CHECKLIST.md` - required evidence, reviewer, decision, and tagging gates.
- `pyproject.toml` - package version, Python requirement, pytest configuration, and Ruff
  configuration.
- Recent repository commits - exact candidate commit at the start of this release-gate attempt.

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
- Do not create a prototype tag unless the release checklist has an explicit `go` decision for the
  exact unchanged candidate commit and selected content versions.

## Blockers

- No complete development checkout was available for the required full verification commands.
- Ruff is not installed in the supplied environment.
- The full pytest suite and synthetic CLI walkthrough remain unverified for this candidate.
- A named independent calculation reviewer and approved exact-candidate record are not present.
- A named qualified independent clinical-content reviewer has not been identified.
- Exact reviewed content versions and reviewer metadata are not recorded in the release checklist.
- PHI review, limitation dispositions, release custodian approval, and the final decision record are
  incomplete.
- The current schema has no explicit supersession relationship or automatic active-version registry.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The logging policy is not yet wired into application or interface failure paths.

These blockers prevent an honest `go`, changelog update, or prototype milestone tag.

## Next exact action

> In a complete development checkout, select the exact candidate commit, run the configured pytest,
> Ruff, and synthetic CLI walkthrough commands, complete independent calculation and
> clinical-content review for exact versions, record PHI and limitation dispositions in
> `docs/PROTOTYPE_RELEASE_CHECKLIST.md`, and create and verify the prototype milestone tag only if
> the unchanged candidate receives an explicit `go`.
