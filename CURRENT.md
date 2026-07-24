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
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The software candidate tested for Day 83 was
  `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` under Python 3.12.1.
- PR #53 merged only the durable verification artifact. Its merge commit is
  `196a351eb48b30a70616d862a640190e0201c9e6`; it did not change implementation or tests.
- The tested candidate failed software verification and remains a release `no-go`.
- Any repair to code, tests, snapshots, goldens, or verification tooling creates a new candidate that
  must be verified from the beginning.

## Current state

The durable evidence is:

`artifacts/verification/full-verification-20260724T082921Z.txt`

Recorded results for candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0`:

- Pytest: 63 failed, 869 passed, 16 skipped; exit status 1.
- Ruff: 284 diagnostics, 261 reported fixable; exit status 1.
- CLI walkthrough: not recorded in the artifact.
- Working tree: ended with untracked `artifacts/` because the evidence file was being created.

The 63 pytest failures reduce to four principal repair areas:

1. **Stale integration fixtures.** The `_order()` helpers in
   `tests/integration/test_renal_dose_matrix.py` and
   `tests/integration/test_renal_safety_invariants.py` construct route and indication concepts with
   codes but no coding systems. Current validation requires both systems, so the workflows stop
   before calculation, repository, rule-engine, failure-handling, and provenance behavior is tested.
   This accounts for 57 listed integration failures.
2. **Stale content review snapshot.** The contract snapshot does not include
   `cefepime_synthetic_fixture.yaml`. The repository must deliberately decide whether the review
   snapshot includes every renal YAML document or only an explicit selected clinical-content set.
3. **Stale cefepime golden JSON.** Canonical regeneration differs from the committed golden at one
   reported byte after the cefepime rule was refactored to the shared exact matcher. The semantic
   difference must be reviewed before any golden regeneration.
4. **Invalid Decimal-context assertions.** Two unit failures compare `decimal.Context` objects with
   `==`. The displayed contexts are equivalent, but object equality is not a useful value comparison
   for this test. Relevant context properties must be compared individually.

Two strict xfails produced misleading XPASS failures because the stale order fixtures already fail
validation for missing route and indication systems:

- conflicting supplied versus declared body-weight type; and
- the famotidine adult minimum-weight limitation.

They do not demonstrate that either known limitation was resolved.

The Ruff result is not yet an actionable repository baseline. `pyproject.toml` declares only the
Ruff target version and line length, while the artifact contains broad rule families such as `UP`,
`FURB`, `DTZ`, `SIM`, `TRY`, `BLE`, `ISC`, and `RUF`. The artifact does not record the exact command
or effective settings. Some diagnostics are legitimate; others flag intentional negative tests,
such as timezone-naive datetimes used to prove rejection.

The evidence record also omits:

- exact pytest and Ruff command lines;
- pytest and Ruff versions;
- operating system and architecture;
- clean-tree status before verification;
- CLI walkthrough output and exit status; and
- an accepted disposition for all 16 placeholder skips.

## Active remediation plan

The controlling plan is
[`docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md`](docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md).
Execute it as separate bounded tasks in this order:

1. Repair only the two integration `_order()` helpers by adding explicit synthetic route and
   indication coding systems.
2. Run only the two affected integration files and confirm the two strict xfails return to their
   intended expected-failure state rather than XPASS.
3. Resolve the synthetic-content snapshot policy intentionally and rerun its contract test.
4. Inspect the semantic cefepime golden diff, then regenerate only if the changed canonical output is
   approved.
5. Replace `Context == Context.copy()` with property-by-property assertions and rerun the focused
   renal service tests.
6. Capture Ruff effective settings, establish the intended ruleset, then fix or narrowly suppress
   only diagnostics produced by that configuration. Do not run a repository-wide automatic fix.
7. Explicitly resolve or accept the 16 placeholder skips and repair the verification evidence
   procedure so every required command, version, environment fact, exit status, and CLI result is
   durable.
8. Create a new candidate commit and rerun full pytest, configured Ruff, and the seven-scenario
   synthetic CLI walkthrough from a clean tree.

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
- Do not weaken a safety test, delete a fixture, overwrite a snapshot, regenerate a golden, or alter
  lint configuration solely to obtain a passing result.
- Do not create a prototype tag unless the release checklist has an explicit `go` decision for the
  exact unchanged candidate commit and selected content versions.

## Blockers

- Candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` failed pytest and Ruff verification.
- Fifty-seven integration failures prevent meaningful full-flow and safety-invariant verification.
- The two strict xfails are currently masked by an earlier validation failure.
- The renal-content snapshot policy is unresolved for synthetic fixtures.
- The cefepime golden semantic change has not been reviewed.
- The Decimal-context tests contain an invalid equality assertion.
- The intended Ruff ruleset and effective configuration have not been established.
- The CLI walkthrough was not recorded.
- The 16 placeholder skips have no accepted release disposition.
- Required environment, command, version, clean-tree, and exit-status evidence is incomplete.
- Independent calculation approval is not recorded for an exact passing candidate.
- Independent clinical-content review is not recorded for every selected exact content version.
- A named qualified independent clinical-content reviewer remains unavailable.
- PHI review, limitation dispositions, release custodian approval, and the final decision record are
  incomplete.
- The current schema has no explicit supersession relationship or automatic active-version registry.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The logging policy is not yet wired into application or interface failure paths.

These blockers prevent an honest `go`, changelog update, or prototype milestone tag.

## Files changed

- `CURRENT.md` - replaced the stale Day 83 pre-verification state with the recorded no-go, failure
  classes, evidence gaps, remediation order, and next action.
- `BACKLOG.md` - records unresolved release-gate decisions and verification work.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - defines bounded repair packages and acceptance gates.
- `AGENTS.md` - adds mandatory release-gate evidence capture rules.
- `docs/TASK_TEMPLATE.md` - adds release/checkpoint verification evidence requirements.

## Additional files inspected

- `AGENTS.md` - repository source hierarchy, verification workflow, and close procedure.
- `BACKLOG.md` - unresolved-work placement rules and existing vertical-slice decisions.
- `docs/TASK_TEMPLATE.md` - bounded task and verification prompt requirements.
- `docs/PROTOTYPE_RELEASE_CHECKLIST.md` - software, reviewer, evidence, and tagging gates.
- `pyproject.toml` - package, pytest, and Ruff configuration.
- `tests/integration/test_renal_dose_matrix.py` - stale `_order()` fixture and strict xfails.
- `tests/integration/test_renal_safety_invariants.py` - stale `_order()` fixture.
- `src/cds/validation/medication.py` - route and indication system sufficiency requirements.
- `artifacts/verification/full-verification-20260724T082921Z.txt` - committed verification output.
- PR #53 metadata - tested candidate, evidence-only change, and merge commit.

## Next exact action

> In a complete development checkout, add explicit synthetic coding systems to `route` and
> `indication` in the `_order()` helpers in `tests/integration/test_renal_dose_matrix.py` and
> `tests/integration/test_renal_safety_invariants.py`. Then run:
>
> ```bash
> python -m pytest tests/integration/test_renal_dose_matrix.py \
>   tests/integration/test_renal_safety_invariants.py -q
> ```
>
> Confirm the missing-system failures are gone and the declared-weight-type conflict and famotidine
> minimum-weight cases are strict XFAIL rather than XPASS. Do not change implementation, snapshots,
> goldens, Ruff configuration, or unrelated tests in that task.
