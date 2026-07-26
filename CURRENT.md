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
- This task is based on current `main`
  `cbb69a486b0a5ba0c52e2126f35a60f6b4a78498`, which contains later steering-document and
  fail-closed implementation changes and must not be described or tagged as the verified candidate.
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

The retained candidate had two strict XFAILs. Both have now been resolved in separate bounded
implementation tasks. A new exact release candidate has not been selected or verified.

## Famotidine adult minimum-weight result

The famotidine rule now configures the documented exact minimum supported adult weight as `40 kg`.
The shared exact matcher enforces that optional medication-specific boundary against the exact
calculation input retained in `RenalFunctionResult.weight_used`.

Patients immediately below `40 kg` receive a structured unsupported-population result with no
recommendation. Patients at and immediately above `40 kg` remain eligible for exact matching. The
former strict XFAIL is now a normal passing integration test. Focused unit and integration
verification produced 108 passed. Full repository verification produced 940 passed with no skips,
XFAILs, or XPASSes. Focused and full Ruff checks passed.

## Completed independent reviews

On 2026-07-26, the project owner confirmed that **Connor Fowler, PharmD** completed the required
independent human reviews for the exact candidate:

- independent calculation review;
- qualified clinical-content review for the selected content set; and
- PHI review of the retained verification artifact.

These completed reviews close the corresponding human-review activities recorded as blocking when
the artifact was generated. They do not change draft clinical-content status or reviewer metadata by
themselves and do not authorize a tag.

## Remaining release blockers

1. Commit exact reviewed status and reviewer metadata for each selected clinical-content version
   where the source files still record `draft`.
2. Select and verify a new exact clean candidate after those changes.
3. Record an explicit final release decision. Create a prototype tag only in a later bounded task
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
  expected-failure markers, or modify lint configuration merely to produce a pass.
- Do not create a prototype tag without an explicit `go` decision for one exact unchanged candidate
  and its selected content versions.

## Files changed in this task

Edited:

- `src/cds/rules/exact_renal_dose.py`
- `src/cds/rules/famotidine.py`
- `tests/unit/rules/test_famotidine.py`
- `tests/integration/test_renal_dose_matrix.py`
- `docs/RELEASE_TEST_DISPOSITIONS.md`
- `docs/PROTOTYPE_RELEASE_CHECKLIST.md`
- `CURRENT.md`
- `BACKLOG.md`

No clinical-content, snapshot, golden, or configuration file is changed.

## Next exact action

After this task is reviewed and merged, create
`docs/record-reviewed-content-metadata`. Record exact reviewed status and Connor Fowler, PharmD as
reviewer for each selected content version covered by the completed qualified review. Do not alter
medication facts, source transcription, renal bands, boundaries, or recommendations.
