# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use a complete repository checkout supplied by a Codespace, local development environment, or
repository-connected Codex task. GitHub is authoritative. A repository-local or temporary isolated
virtual environment may be created, and project-declared development dependencies may be installed from
`pyproject.toml`. Do not install dependencies globally or reconstruct an incomplete checkout as
acceptance evidence.

## Roadmap position

- Days 1-82 are complete.
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The original Day 83 candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` remains a release
  `no-go`; this focused acceptance result does not certify a new release candidate.
- PR #55 repaired the bounded route and indication integration fixtures.
- PR #58 merged canonical non-exponent renal-value normalization as
  `86a14d397b3e0f89e5a1f56f164933d45b76d627`.
- **INT-2 renal integration acceptance is complete.**

## INT-2 acceptance result

Verified in a complete, clean checkout of `cc2c4226c768c81fbdf9de67ce9e0976eee76deb` at `2026-07-25T03:19:31Z`.

Environment:

- `Python 3.12.1`
- `pytest 9.1.1`
- Python source: `repository .venv`

Exact command:

```bash
python -m pytest -q \
  tests/integration/test_renal_dose_matrix.py \
  tests/integration/test_renal_safety_invariants.py
```

Exact result:

- `117 passed, 2 xfailed in 14.05s`
- Exit status: `0`
- The 39 previously failing parameterized `renal_value` textual comparisons now pass.
- Boundary band selection and exact serialized renal-value assertions pass without expectation changes.
- `test_declared_weight_type_conflict_fails_closed` remains strict XFAIL.
- `UNSUP-FAM-WEIGHT` remains strict XFAIL.
- No unrelated failure, error, XPASS, or skip occurred in the two focused files.
- The mismatch was resolved by canonical output normalization already present on `main`; this acceptance
  task changed no implementation, fixture, expected value, safety boundary, public contract, or XFAIL
  marker.

## Remaining repair areas

1. **Work Package 2:** deliberately resolve the renal-content snapshot scope and run only the focused
   snapshot and synthetic-fixture eligibility verification required by the remediation plan.
2. Review the cefepime golden semantic diff before any regeneration.
3. Correct the Decimal-context preservation assertions in the focused renal service tests.
4. Establish and remediate the intended Ruff baseline without repository-wide automatic fixes.
5. Resolve placeholder skips and repair durable release-evidence capture.
6. Select and fully verify a new release candidate only after the preceding work packages are complete.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate before calculation or rule matching; unsupported or insufficient cases fail closed.
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

- The renal-content snapshot policy is unresolved for synthetic fixtures.
- The cefepime golden semantic difference has not been reviewed.
- Decimal-context tests contain invalid object-equality assertions.
- The intended Ruff ruleset and effective configuration remain unresolved.
- Placeholder-skip dispositions, CLI evidence, clean candidate evidence, independent calculation
  approval, qualified content review, PHI review, release-custodian approval, and a final decision record
  remain incomplete.
- Existing known clinical and architecture limitations remain outside this acceptance task, including
  weight-type conflict handling, the famotidine adult minimum-weight boundary, content supersession,
  standalone CLI composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

- `CURRENT.md` - records the successful, reproducible INT-2 acceptance result and the next separate work
  package.

No production code, tests, fixtures, content, snapshots, goldens, workflow configuration, or safety
invariant documentation changed.

## Additional files inspected

None beyond the files named by the INT-2 acceptance task and repository/PR metadata needed to verify the
current `main` commit and publish this documentation-only result.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute a separate bounded task for **Work Package 2 —
Resolve the renal-content snapshot scope**. Do not begin that work in the INT-2 pull request.
