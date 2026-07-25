# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the complete repository checkout supplied by the execution environment. GitHub is the authoritative
source and destination. Do not search broadly for alternate checkouts, reconstruct an incomplete tree as
acceptance evidence, install missing dependencies, or substitute another test runner.

## Roadmap position

- Days 1-82 are complete.
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The original Day 83 candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` remains a release
  `no-go`.
- PR #55 repaired the bounded route and indication integration fixtures.
- PR #58 merged canonical non-exponent renal-value normalization as
  `86a14d397b3e0f89e5a1f56f164933d45b76d627`.
- **INT-2 renal integration acceptance is still pending execution in a complete checkout.**

## Current state

The repository root now includes `complete-int2-renal-acceptance.sh`, a fail-closed acceptance runner for
the remaining INT-2 gate.

The runner:

- requires a complete, clean `cfowla/cds-platform` checkout with authenticated `git`, `gh`, and Python;
- verifies that the reviewed renal-normalization baseline remains an ancestor of current `main`;
- permits only `CURRENT.md` and the runner itself as post-baseline changes before acceptance execution;
- runs exactly:

  ```bash
  python -m pytest -q \
    tests/integration/test_renal_dose_matrix.py \
    tests/integration/test_renal_safety_invariants.py
  ```

- requires exactly `117 passed, 2 xfailed`, with no failure, error, skip, or XPASS result;
- confirms the two existing strict XFAIL markers remain present;
- changes only `CURRENT.md` after successful verification;
- creates `feature/complete-int2-renal-acceptance`, opens a focused pull request, verifies its scope and
  review state, and squash-merges only when the head commit is unchanged and GitHub permits merging; and
- makes no repository change when the focused gate fails.

The two strict XFAIL cases currently recognized by the focused integration files are:

- `test_declared_weight_type_conflict_fails_closed`; and
- `UNSUP-FAM-WEIGHT`.

No Infinity or NaN strict-XFAIL scenarios were found in the two focused integration files, so the runner
does not fabricate such an acceptance requirement.

## Verification for this publication task

Performed against the exact runner content before repository publication:

```bash
bash -n complete-int2-renal-acceptance.sh
```

Result: exit status `0`.

Runner SHA-256:

`bb789e0642d8fb4349984a7a60c2366383842046d2d04995a313772039155a70`

The focused pytest acceptance command was not run during this publication task. Therefore, INT-2 is not
marked complete and no focused test result is recorded here.

## Remaining repair areas

1. Execute the root acceptance runner in a complete Codespace checkout and allow it to record and merge
   INT-2 only if the focused result is exactly reproducible.
2. Resolve the synthetic-content snapshot policy intentionally and rerun its focused contract test.
3. Inspect the semantic cefepime golden diff, then regenerate only if the changed canonical output is
   approved.
4. Replace invalid `Context == Context.copy()` assertions with property-by-property comparisons and
   rerun the focused renal service tests.
5. Capture Ruff effective settings, establish the intended ruleset, then fix or narrowly suppress only
   diagnostics produced by that configuration.
6. Resolve or explicitly accept the placeholder skips and repair complete release-evidence capture.
7. Select and fully verify a new release candidate only after the preceding work packages are complete.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Draft and retired clinical content are not eligible for dosing recommendations.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers, coding systems, units, and case exact; do not infer, alias, convert, or normalize them.
- Preserve exact Decimal behavior and numeric-string serialization without binary floating-point
  conversion or clinical rounding.
- Preserve public imports, exception behavior, serialization contracts, clinical content, and safety
  boundaries unless a separate task explicitly authorizes a change.
- Do not weaken tests, remove fixtures, overwrite snapshots, regenerate goldens, alter XFAIL markers, or
  modify lint configuration merely to produce a pass.
- Do not create a prototype tag without an explicit `go` decision for one exact unchanged candidate and
  its selected content versions.

## Blockers

- The canonical renal-value change has not yet passed the required focused integration command in a
  complete checkout.
- The renal-content snapshot policy is unresolved for synthetic fixtures.
- The cefepime golden semantic difference has not been reviewed.
- Decimal-context tests contain invalid object-equality assertions.
- The intended Ruff ruleset and effective configuration remain unresolved.
- Placeholder-skip dispositions, CLI evidence, clean candidate evidence, independent calculation
  approval, qualified content review, PHI review, release-custodian approval, and a final decision record
  remain incomplete.
- Existing known clinical and architecture limitations remain outside this task, including weight-type
  conflict handling, the famotidine adult minimum-weight boundary, content supersession, standalone CLI
  composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

- `complete-int2-renal-acceptance.sh` - adds the complete-checkout INT-2 acceptance, documentation,
  pull-request, and guarded merge workflow.
- `CURRENT.md` - records the runner, its safeguards, publication verification, unresolved acceptance
  state, and the exact next action.

No production code, test, fixture, clinical content, snapshot, golden, workflow configuration, or safety
invariant documentation changed.

## Additional files inspected

- `tests/integration/test_renal_dose_matrix.py` - confirmed the expected focused count and the two strict
  XFAIL cases enforced by the runner.
- `tests/integration/test_renal_safety_invariants.py` - confirmed the second focused acceptance file and
  absence of additional strict non-finite XFAIL scenarios.
- `src/cds/services/renal.py` - confirmed the canonical renal-value normalization baseline checked by the
  runner.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - confirmed INT-2 must complete before the separate renal
  snapshot-policy work.

## Next exact action

From a complete Codespace checkout after pulling current `main`, run:

```bash
git switch main
git pull --ff-only
chmod +x complete-int2-renal-acceptance.sh
./complete-int2-renal-acceptance.sh
```

Do not begin Work Package 2 unless that runner records and merges a successful INT-2 acceptance result.
