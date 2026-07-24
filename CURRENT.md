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

The durable failed-candidate evidence remains:

`artifacts/verification/full-verification-20260724T082921Z.txt`

Recorded results for candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0`:

- Pytest: 63 failed, 869 passed, 16 skipped; exit status 1.
- Ruff: 284 diagnostics, 261 reported fixable; exit status 1.
- CLI walkthrough: not recorded in the artifact.

Work package 1 from
[`docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md`](docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md) is now
implemented on `agent/repair-integration-order-systems`:

- `tests/integration/test_renal_dose_matrix.py` defines stable synthetic route and indication coding
  systems and supplies them from `_order()`.
- `tests/integration/test_renal_safety_invariants.py` defines the same stable synthetic systems and
  supplies them from `_order()`.
- Existing route and indication codes remain unchanged and continue to come from the selected renal
  content.
- `src/cds/validation/medication.py` was not changed; its requirement for explicit route and indication
  systems remains intact.

The focused integration verification is still pending. The fixture repair must not be treated as a
completed release-remediation gate until the prescribed tests run in a complete development checkout.

## Verification

Repository probe:

```bash
git rev-parse --show-toplevel
```

Result: exit status 128 from `/mnt/data`; no repository checkout was supplied.

Test-runner probe:

```bash
python -m pytest --version
```

Result: `pytest 9.0.2`.

Required focused command:

```bash
python -m pytest tests/integration/test_renal_dose_matrix.py \
  tests/integration/test_renal_safety_invariants.py -q
```

This command was not run because no complete repository checkout or local connector-to-filesystem
materialization path was available. No dependency was installed, no substitute test runner was used,
and no pytest passing claim is made.

GitHub branch comparison against `main` reports only:

- `tests/integration/test_renal_dose_matrix.py`: 7 additions, 2 deletions.
- `tests/integration/test_renal_safety_invariants.py`: 7 additions, 2 deletions.

The inspected commit patches contain only the two test-only constants and their use in the route and
indication `CodeableConcept` constructors.

## Active remediation plan

The controlling plan remains
[`docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md`](docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md).
Execute it as separate bounded tasks in this order:

1. Run the two focused integration files and confirm the repaired fixtures reach their intended test
   stages without `missing_required_route_system` or `missing_required_indication_system` failures.
2. Confirm `test_declared_weight_type_conflict_fails_closed` and `UNSUP-FAM-WEIGHT` are strict XFAIL,
   not XPASS.
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

- The focused integration command has not yet run against the repaired fixtures.
- The two strict xfail outcomes have not yet been re-established with executable evidence.
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

- `tests/integration/test_renal_dose_matrix.py` - adds explicit synthetic route and indication coding
  systems to the integration `_order()` fixture.
- `tests/integration/test_renal_safety_invariants.py` - adds the same explicit synthetic systems to the
  safety-invariant `_order()` fixture.
- `CURRENT.md` - replaces the stale next-action state with the implemented fixture repair, honest
  verification limitation, and focused rerun action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded task structure, execution context, verification, and close
  procedure.
- `docs/SAFETY_INVARIANTS.md` - prototype, synthetic-data, validation, fail-closed, and scope
  constraints.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - work package 1 scope and acceptance gate.
- `src/cds/validation/medication.py` - confirms explicit route and indication systems are required and
  that the validator should not be weakened.
- The two focused GitHub commit patches - confirms no unrelated file content changed.

## Next exact action

> In a complete development checkout at the branch containing this repair, run:
>
> ```bash
> python -m pytest tests/integration/test_renal_dose_matrix.py \
>   tests/integration/test_renal_safety_invariants.py -q
> ```
>
> Confirm there are no valid-fixture failures for `missing_required_route_system` or
> `missing_required_indication_system`, and confirm
> `test_declared_weight_type_conflict_fails_closed` and `UNSUP-FAM-WEIGHT` are strict XFAIL rather
> than XPASS. Do not change implementation, content, snapshots, goldens, Ruff configuration, or
> unrelated tests during that verification.
