# Current Project State

## Execution mode

- Repository: `cfowla/cds-platform`
- Authoritative release branch: `main`
- Active coding branch: `development/unrestricted-implementation`
- Prototype remains nonclinical and is not authorized for patient-care use.
- Repository files, not prior chat history, are the durable source of truth.

## Branch policy

The active coding branch is an implementation workspace, not a release candidate or verification checkpoint.
Development on this branch may proceed without satisfying release, checkpoint, acceptance, regression, lint,
coverage, snapshot, golden-case, clean-tree, or evidence-capture gates after each task or commit.

Permitted intermediate states include:

- failing, missing, stale, or temporarily disabled non-safety verification;
- incomplete features, partial migrations, broad refactors, and temporary incompatibilities;
- implementation changes without corresponding tests in the same commit;
- deferred full-suite, Ruff, CLI, snapshot, golden, and release-capture execution; and
- rapid iteration across multiple related files or work packages without one bounded deliverable per commit.

Verification results must still be reported honestly when checks are run. No passing, release-ready, clinically
validated, or production-ready claim may be made without the applicable verification being completed against an
exact candidate.

## Non-negotiable boundaries

The relaxed coding policy does not waive `PROJECT_CHARTER.md` or `docs/SAFETY_INVARIANTS.md`. In particular:

- do not use the prototype for direct clinical care;
- use synthetic or properly de-identified data only;
- preserve fail-closed behavior for unsupported or insufficient clinical inputs;
- do not fabricate clinical values, silently infer required context, or resolve content defects silently;
- preserve inspectable, versioned clinical content and required clinical-content review; and
- do not describe an unverified branch state as a release candidate.

Temporary test failures may exist during implementation, but intentional weakening of a safety invariant requires
an explicit charter change rather than relying on this branch policy.

## Roadmap position

- Days 1-82: complete.
- Day 83 release gate: incomplete.
- The historical Day 83 candidate remains a release `no-go`.
- Work Packages 1-7 completed bounded remediation and retained verification evidence for candidate
  `179c22842caa45d3a1c5e8c04b0bd83025418545`.
- Current development is no longer blocked on selecting or preserving an unchanged release candidate.

## Main branch release state

Current `main` remains unverified for release. Its prior verification blocker and `no-go` status remain relevant
only when selecting a future exact candidate for release or checkpoint verification. Development work should occur
on `development/unrestricted-implementation` until the project owner deliberately selects a candidate for
hardening and verification.

## Completion standard on the coding branch

A coding task is complete when the requested implementation or documentation change has been committed to the
active coding branch. Tests, lint, integration checks, snapshots, goldens, and release evidence are optional unless
the task explicitly requests them or they are needed to understand the implementation.

When verification is skipped, blocked, or failing, record that fact briefly; do not stop otherwise-authorized
coding solely to satisfy a verification gate.

## Next exact action

Continue implementation on `development/unrestricted-implementation` according to project priorities. Create a
separate hardening or release-candidate branch only when the project owner explicitly chooses to reconcile tests,
resolve regressions, freeze behavior, and run full verification against an exact commit.
