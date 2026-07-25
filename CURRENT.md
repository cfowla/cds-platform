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
- **INT-2 renal integration acceptance remains complete.**
- **Work Package 2 renal-content snapshot scope is complete.**

## Work Package 2 result

Verified from current `main` commit `a54be8efef7b4457f5078f9c32be8c9742052474` in a complete GitHub-hosted checkout
at `2026-07-25T03:47:03Z`.

Policy decision:

- The renal review contract uses an **explicit selected-content snapshot**.
- Selected clinical documents are enumerated by `_EXPECTED_DOCUMENTS` in
  `tests/contract/test_renal_content_snapshots.py`.
- The loader reads only those enumerated filenames and fails explicitly when a selected document is
  missing.
- `cefepime_synthetic_fixture.yaml` remains present but intentionally outside the clinical-review
  snapshot.
- The synthetic fixture remains separately covered as structurally loadable, draft, and ineligible for
  recommendation matching.

Environment:

- `Python 3.12.13`
- `pytest 9.1.1`
- Python source: GitHub Actions `actions/setup-python` isolated runner

Baseline command:

```bash
python -m pytest tests/contract/test_renal_content_snapshots.py -q
```

Baseline result before the bounded test change:

- `1 failed, 1 passed in 0.21s`
- Exit status: `1`
- The failure was caused by the directory-wide loader including the separately maintained synthetic
  fixture that was intentionally absent from `_EXPECTED_DOCUMENTS`.

Focused verification commands:

```bash
python -m pytest tests/contract/test_renal_content_snapshots.py -q
python -m pytest   tests/integration/test_cefepime_end_to_end.py::test_yaml_loaded_draft_content_remains_ineligible_after_validated_calculation   -q
```

Exact results:

- Snapshot contract: `3 passed in 0.19s`; exit status `0`.
- Synthetic-fixture draft/eligibility test: `1 passed in 0.08s`; exit status `0`.
- The contract names and helper structure now make the selected scope explicit.
- The synthetic fixture still exists and loads through the YAML repository in the focused integration
  test.
- Its review status remains `draft`, rule evaluation remains `incomplete`, and no recommendation is
  emitted.

## Remaining repair areas

1. **Work Package 3:** review the cefepime golden semantic diff before any regeneration.
2. Correct the Decimal-context preservation assertions in the focused renal service tests.
3. Establish and remediate the intended Ruff baseline without repository-wide automatic fixes.
4. Resolve placeholder skips and repair durable release-evidence capture.
5. Select and fully verify a new release candidate only after the preceding work packages are complete.

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

- `tests/contract/test_renal_content_snapshots.py` - defines the explicit selected-content loader and
  assertions while keeping the synthetic fixture outside the clinical-review snapshot.
- `CURRENT.md` - records the policy decision, baseline, focused verification, bounded scope, and next work
  package.

No clinical YAML, production implementation, snapshot data, golden files, safety behavior, eligibility
rule, public contract, or lint configuration changed.

## Additional files inspected

- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` - confirmed the fixture is explicitly synthetic,
  draft, and not eligible for rule matching; it was not edited.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - confirmed Work Package 2 permits the explicit
  selected-content policy and requires separate synthetic-fixture coverage.
- `tests/integration/test_cefepime_end_to_end.py` - identified the focused test that loads the fixture,
  proves draft status, and verifies recommendation ineligibility after validated calculation.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute a separate bounded task for **Work Package 3 —
Review the cefepime golden semantic diff**. Do not regenerate or overwrite any golden before recording the
exact changed field and its semantic meaning.