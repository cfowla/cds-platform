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
- Current `main` is `ce5e68bd33a5f121e02f8d061a1a347f8b02b040`; that later commit adds
  the retained evidence artifact and must not be described or tagged as the verified candidate.
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

The two strict XFAILs remain unresolved and blocking:

1. conflicting supplied versus declared weight type is not rejected before calculation;
2. the famotidine adult minimum-weight boundary is not enforced in the full flow.

## Completed independent reviews

On 2026-07-26, the project owner confirmed that **Connor Fowler, PharmD** completed the required
independent human reviews for the exact candidate:

- independent calculation review;
- qualified clinical-content review for the selected content set; and
- PHI review of the retained verification artifact.

These completed reviews close the corresponding human-review activities recorded as blocking when
the artifact was generated. They do not resolve the two fail-closed implementation gaps, do not
change draft clinical-content status or reviewer metadata by themselves, and do not authorize a tag.

## Remaining release blockers

1. Resolve and independently verify the supplied-versus-declared weight-type conflict.
2. Resolve and independently verify the famotidine adult minimum-weight boundary.
3. Commit exact reviewed status and reviewer metadata for each selected clinical-content version
   where the source files still record `draft`.
4. Select and verify a new exact clean candidate after those changes.
5. Record an explicit final release decision. Create a prototype tag only in a later bounded task
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

Edited only:

- `CURRENT.md`
- `BACKLOG.md`
- `docs/PROTOTYPE_RELEASE_CHECKLIST.md`

No production, test, clinical-content, snapshot, golden, or configuration file is changed.

## Next exact action

After this documentation reconciliation is reviewed and merged, create
`fix/fail-closed-weight-type-conflict`. Make conflicting supplied and declared weight types fail
before calculation, convert the corresponding strict XFAIL to a normal passing test, and run the
focused integration verification. Do not begin a generic rule-engine feature.
