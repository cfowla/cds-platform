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
- **Day 83 - Tag the prototype milestone remains incomplete.**
- **Work Packages 1-7 software remediation and verification are complete.**
- The verified software candidate is
  `179c22842caa45d3a1c5e8c04b0bd83025418545`.
- Current `main` is `d7aa94e37d122f6d484c8194f7d68158a07c63b2`; it contains the retained
  evidence and reconciled steering documents and must not be described or tagged as the verified
  candidate.
- The overall prototype release decision remains **no-go**.

## Work Package 7 result

The retained evidence is
`artifacts/verification/full-verification-20260726T023944Z.txt`.

The unchanged candidate passed the complete software gate:

- Pytest: 935 passed, 2 strict XFAILs; exit status 0.
- Ruff: `All checks passed!`; exit status 0.
- CLI walkthrough: 7 synthetic scenarios verified; exit status 0.
- Pre-verification working tree: clean.
- Post-verification tracked candidate state: unchanged.
- Overall software verification: **PASS**.

The retained candidate had two strict XFAILs. This task resolves the supplied-versus-declared
weight-type conflict. The famotidine adult minimum-weight boundary remains unresolved and blocking.

## Weight-type conflict result

`validate_patient_structure` now rejects an explicitly supplied `Patient.actual_body_weight` when
the caller declares it as ideal, adjusted, or other weight. The structured
`conflicting_weight_type` error is returned during initial validation, before content lookup,
calculation, or rule evaluation, and no recommendation is produced.

The former strict XFAIL is now a normal passing integration test. Focused validation and integration
verification produced 286 passed and 1 unrelated strict XFAIL. Full repository verification
produced 936 passed and the same famotidine strict XFAIL. Ruff passed for the changed files and the
full repository.

## Completed independent reviews

On 2026-07-26, the project owner confirmed that **Connor Fowler, PharmD** completed the required
independent human reviews for the exact candidate:

- independent calculation review;
- qualified clinical-content review for the selected content set; and
- PHI review of the retained verification artifact.

These completed reviews close the corresponding human-review activities recorded as blocking when
the artifact was generated. They do not resolve the remaining fail-closed implementation gap, do not
change draft clinical-content status or reviewer metadata by themselves, and do not authorize a tag.

## Remaining release blockers

1. Resolve and independently verify the famotidine adult minimum-weight boundary.
2. Commit exact reviewed status and reviewer metadata for each selected clinical-content version
   where the source files still record `draft`.
3. Select and verify a new exact clean candidate after those changes.
4. Record an explicit final release decision. Create a prototype tag only in a later bounded task
   after an explicit `go`.

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

## Files changed in this task

Edited:

- `src/cds/validation/patient.py`
- `tests/unit/validation/test_patient.py`
- `tests/integration/test_renal_dose_matrix.py`
- `docs/RELEASE_TEST_DISPOSITIONS.md`
- `docs/PROTOTYPE_RELEASE_CHECKLIST.md`
- `CURRENT.md`
- `BACKLOG.md`

No clinical-content, snapshot, golden, or configuration file is changed.

## Next exact action

After this task is reviewed and merged, create
`fix/fail-closed-famotidine-adult-weight-boundary`. Make patients below the exact supported adult
minimum weight receive no recommendation, convert the remaining strict XFAIL to a normal passing
test, and run the focused integration verification. Do not begin a generic rule-engine feature.
