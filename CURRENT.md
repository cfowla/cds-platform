# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use a complete repository checkout supplied by a Codespace, local development environment, or
repository-connected Codex task. GitHub is authoritative.

A generic Work or artifact sandbox containing only directories such as `work/` and `outputs/`, without
`.git`, Git, or Bash, cannot execute repository acceptance. Stop there rather than reconstructing an
incomplete checkout.

In a complete checkout, a repository-local or temporary isolated virtual environment may be created.
Project-declared development dependencies may be installed from `pyproject.toml`; do not install them
globally. Record the Python and test-tool versions used. If virtual-environment creation or declared
dependency installation fails, stop without changing repository files.

## Roadmap position

- Days 1-82 are complete.
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The original Day 83 candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` remains a release
  `no-go`.
- PR #55 repaired the bounded route and indication integration fixtures.
- PR #58 merged canonical non-exponent renal-value normalization as
  `86a14d397b3e0f89e5a1f56f164933d45b76d627`.
- PR #59 added the root INT-2 acceptance runner.
- **INT-2 renal integration acceptance remains pending execution in a complete checkout.**

## Current state

The root `complete-int2-renal-acceptance.sh` runner now supports dependency bootstrap in a complete
checkout. It:

- requires Git and a complete checkout, but does not require GitHub CLI until after focused tests pass;
- identifies the repository from the `origin` remote rather than using GitHub CLI;
- verifies current remote `main` contains the reviewed renal normalization baseline;
- reports dirty paths using shell-safe quoting instead of returning only a generic clean-tree error;
- checks out exact current `origin/main` in detached mode;
- prefers `.venv/bin/python` when available;
- otherwise creates a temporary isolated virtual environment and installs only `.[dev]` from
  `pyproject.toml`, which provides the declared `pytest` and Ruff dependencies;
- runs exactly:

  ```bash
  python -m pytest -q \
    tests/integration/test_renal_dose_matrix.py \
    tests/integration/test_renal_safety_invariants.py
  ```

- requires exactly `117 passed, 2 xfailed`, with no failure, error, skip, or XPASS result;
- confirms `test_declared_weight_type_conflict_fails_closed` and `UNSUP-FAM-WEIGHT` remain strict XFAIL;
- requires authenticated GitHub CLI only for branch, pull-request, review, check, and guarded merge steps;
- changes only `CURRENT.md` after successful verification; and
- makes no repository change when acceptance fails.

No Infinity or NaN strict-XFAIL scenarios exist in the two focused integration files, so the runner does
not invent such a requirement.

## Verification for this execution-support task

Performed against the revised runner before publication:

```bash
bash -n complete-int2-renal-acceptance.sh
```

Result: exit status `0`.

The focused renal pytest acceptance command was not run for this execution-support task. Therefore,
INT-2 is not marked complete here.

## Remaining repair areas

1. Execute the root acceptance runner in a fresh Codespace, local checkout, or repository-connected Codex
   environment and allow it to record and merge INT-2 only if the exact focused result is reproducible.
2. Resolve the synthetic-content snapshot policy intentionally and rerun its focused contract test.
3. Inspect the semantic cefepime golden diff, then regenerate only if the changed canonical output is
   approved.
4. Replace invalid `Context == Context.copy()` assertions with property-by-property comparisons and
   rerun the focused renal service tests.
5. Establish and remediate the intended Ruff baseline without repository-wide automatic fixes.
6. Resolve placeholder skips and repair complete release-evidence capture.
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

- `complete-int2-renal-acceptance.sh` - permits declared dependency bootstrap, improves environment and
  dirty-tree diagnostics, and postpones GitHub CLI requirements until publication.
- `CURRENT.md` - records the corrected execution model and exact next action.

No production code, integration test, fixture, clinical content, snapshot, golden, XFAIL marker, workflow,
or safety-invariant document changed.

## Additional files inspected

- `AGENTS.md` - confirmed repository-connected complete checkouts are preferred and that declared test
  dependencies may be installed when focused verification requires them.
- `pyproject.toml` - confirmed `pytest>=8.0` and `ruff>=0.5` are declared under the `dev` extra.
- `.gitignore` - confirmed `.venv/`, test caches, build output, and package metadata are ignored.

## Next exact action

Create a fresh Codespace from current `main`, or start a repository-connected Codex task. Then run:

```bash
git switch main
git pull --ff-only
bash complete-int2-renal-acceptance.sh
```

Do not run `chmod +x`; changing the tracked executable bit makes the clean-tree gate fail. Do not begin
Work Package 2 unless the runner records and merges a successful INT-2 acceptance result.
