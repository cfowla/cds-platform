# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use a complete repository checkout supplied by a Codespace, local development environment, or
repository-connected Codex task for release-candidate verification. GitHub is authoritative. For a
bounded focused task, `docs/TASK_TEMPLATE.md` permits a connector-materialized verification checkout
containing only the named files and concretely required imports. A bounded checkout may prove the
focused deliverable but does not replace clean, hash-verified release-candidate evidence.

A repository-local or temporary isolated virtual environment may be created, and project-declared
development dependencies may be installed from `pyproject.toml`. Do not install dependencies globally.

## Roadmap position

- Days 1-82 are complete.
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The original Day 83 candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` remains a release
  `no-go`; this bounded tooling task does not select or certify a new candidate.
- **INT-2 renal integration acceptance remains complete.**
- **Work Packages 2-6 are complete.**
- **Work Package 7 remains next:** select one new exact candidate and perform the full software gate
  with the repaired evidence procedure.

## Work Package 6 result

Implemented from current `main` base commit
`00bf1bdccff19934bf069bf6d899bb358e48c25c`.

Placeholder disposition:

- The prior artifact's 16 skips came from 16 identical placeholder modules that asserted no
  behavior.
- `docs/RELEASE_TEST_DISPOSITIONS.md` maps every placeholder path to existing behavior-specific
  contract, integration, mapper, repository, serialization, or validation coverage.
- All 16 placeholder modules were removed. Their removal is not counted as a passing test, and future
  components require behavior-specific tests rather than reserved skipped paths.
- The two known strict XFAIL signals remain explicit, unresolved nonclinical prototype limitations:
  weight-type conflict handling and the famotidine adult minimum-weight boundary.

Durable evidence capture:

- `tools/capture_release_verification.py` requires a named release custodian and a clean initial
  working tree.
- It records the exact commit and branch, package version, repository root, Python executable,
  Python/pytest/Ruff versions, operating system, architecture, timezone-aware timestamps, test
  dispositions, and durable artifact path.
- It records each exact verification command before complete combined output, along with start,
  completion, and exit status, and it continues through all three commands after a failure.
- It requires the exact seven-scenario CLI confirmation, rejects artifact overwrite, verifies that
  the candidate SHA and tracked tree remain unchanged, and rejects unexpected generated files.
- It marks PHI review, independent calculation review, qualified clinical-content review, and the
  final release decision as blocking manual gates. Generated evidence must be reviewed before commit.

No production implementation, clinical content, public contract, snapshot, golden, lint policy,
strict-XFAIL behavior, or clinical safety boundary changed.

## Verification

The evidence runner, its tests, disposition record, and `pyproject.toml` were materialized in a
bounded checkout. An isolated virtual environment installed only the repository-declared pytest and
Ruff development dependencies.

Final targeted verification:

```bash
python -m pytest tests/unit/tools/test_capture_release_verification.py -q
python -m ruff check tools/capture_release_verification.py \
  tests/unit/tools/test_capture_release_verification.py --config pyproject.toml
```

Result:

- Focused pytest exit status: 0; 3 tests passed.
- Focused Ruff exit status: 0; `All checks passed!`.
- The disposition inventory contains exactly 16 unique placeholder paths.

The complete test suite and release commands were deliberately not run because Work Package 6
changes verification tooling and therefore cannot select its own release candidate. No new durable
candidate artifact was generated.

## Remaining repair and review areas

1. **Work Package 7:** select the exact clean commit produced after this merge, run
   `tools/capture_release_verification.py` in a complete repository environment, and review every
   result without changing the candidate.
2. Complete independent calculation review for that exact candidate.
3. Complete qualified independent clinical-content review for every selected exact content version.
4. Complete PHI review of retained evidence and record release-custodian approval.
5. Record an explicit `go` or `no-go`; tag the prototype milestone only in a later bounded task after
   an explicit `go`.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate before calculation or rule matching; unsupported or insufficient cases fail closed.
- Keep identifiers, coding systems, units, and case exact; do not infer, alias, convert, or normalize
  them.
- Preserve exact Decimal behavior and numeric-string serialization without binary floating-point
  conversion or clinical rounding.
- Preserve public imports, exception behavior, serialization contracts, clinical content, and safety
  boundaries unless a separate task explicitly authorizes a change.
- Do not weaken tests, remove required fixtures, overwrite unrelated snapshots or goldens, alter
  strict XFAIL markers, or modify lint configuration merely to produce a pass.
- Do not create a prototype tag without an explicit `go` decision for one exact unchanged candidate
  and its selected content versions.

## Blockers

- A new exact candidate has not yet been selected or run through the repaired full evidence
  procedure.
- Independent calculation approval, qualified content review, PHI review, release-custodian approval,
  and a final decision record remain incomplete.
- Known limitations still include weight-type conflict handling, the famotidine adult minimum-weight
  boundary, content supersession, standalone CLI composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

Created:

- `tools/capture_release_verification.py`
- `tests/unit/tools/test_capture_release_verification.py`
- `docs/RELEASE_TEST_DISPOSITIONS.md`

Edited:

- `docs/PROTOTYPE_RELEASE_CHECKLIST.md`
- `CURRENT.md`

Deleted:

- The 16 exact placeholder test modules inventoried in
  `docs/RELEASE_TEST_DISPOSITIONS.md`.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded-task, evidence, and close-procedure requirements.
- `docs/SAFETY_INVARIANTS.md` - prototype, synthetic-data, auditability, and safety constraints.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - Work Package 6 scope and acceptance gate.
- `docs/PROTOTYPE_RELEASE_CHECKLIST.md` - required environment, command, disposition, and review
  fields.
- `artifacts/verification/full-verification-20260724T082921Z.txt` - exact list of 16 placeholder
  skips and the incomplete prior evidence structure.
- `pyproject.toml` - declared Python, pytest, Ruff, and lint configuration.
- `.gitignore` - confirmed generated verification artifacts are visible for review rather than
  silently ignored.
- `examples/cli_walkthrough.py` and `tests/unit/interfaces/test_cli_walkthrough.py` - exact seven
  scenario success contract.
- Directly corresponding concrete contract, integration, application, mapper, repository,
  serialization, and validation tests - confirmed each placeholder was redundant.
- `project_sources/01-Architect-for-CDS.txt` - confirmed that the task changes verification tooling,
  not clinical-layer boundaries.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute Work Package 7 as a separate release-candidate
verification task: select the exact clean post-merge commit, run
`tools/capture_release_verification.py --release-custodian "<name and role>"` in a complete repository
environment, retain and review the generated artifact, and do not modify the candidate during
verification.
