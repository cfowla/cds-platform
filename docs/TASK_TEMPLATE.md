# CDS Task Template

Use this template for implementation work. Copy it into a new task, replace every placeholder, and remove sections that do not apply. Do not add project history merely to make the prompt look complete.

## Branch mode

State which mode applies:

- **Coding mode** — default on `development/unrestricted-implementation`. Optimize for implementing the requested project behavior. Verification is advisory and non-blocking unless the task explicitly makes a specific check part of the deliverable.
- **Hardening mode** — used when reconciling tests, lint, contracts, snapshots, goldens, compatibility, or technical debt before selecting a candidate.
- **Release-verification mode** — used only for an exact frozen candidate. The release or checkpoint requirements below are mandatory in this mode.

Do not apply release-candidate preservation rules to ordinary coding-mode work.

## Read first

Read the files needed to understand and implement this task:

- [`docs/SAFETY_INVARIANTS.md`](SAFETY_INVARIANTS.md)
- `<active state or prior-note file>`
- `<directly relevant implementation file>`
- `<directly relevant test or contract file, when useful>`

Treat the named repository files as authoritative. Do not reconstruct requirements from prior chat history.

Read [`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md) when the task changes clinical scope, supported medications or populations, safety behavior, clinical content requirements, intended users, or interfaces. Read [`FIRST_VERTICAL_SLICE.md`](../FIRST_VERTICAL_SLICE.md) when the task changes the frozen renal feature contract.

In coding mode, inspect any additional repository files needed to implement a coherent change. Avoid broad review that does not contribute to the requested work, but do not artificially restrict file access when dependencies, architecture, migrations, or cross-cutting behavior require it.

## Execution context

- Use the repository checkout supplied by the execution environment when available.
- The GitHub connector may be used for repository reads and writes.
- In coding mode, a partial local checkout, unavailable test runner, absent development dependency, dirty working tree, or inability to execute the full suite does not block implementation.
- Do not claim checks passed unless they were actually run.

## Deliverable

Implement **`<precise deliverable or coherent development objective>`**.

Done when: `<observable implementation or documentation condition>`.

Coding-mode tasks may include multiple related changes, broad refactors, temporary compatibility breaks, partial migrations, or follow-on scaffolding when these form one coherent development objective.

## Required behavior

- `<observable requirement 1>`
- `<observable requirement 2>`
- `<observable requirement 3>`

For CDS behavior, state how missing, invalid, unsupported, or indeterminate inputs must be represented. Do not rely on vague requirements such as “robust,” “safe,” or “production-ready” without concrete behavior.

## Non-goals

- Do not `<excluded adjacent task or feature>`.
- Do not use real patient data or protected health information.
- Do not authorize direct clinical use.

Include other non-goals only when they materially constrain the task. Coding mode does not require the smallest possible diff and does not prohibit speculative scaffolding when the task explicitly requests it.

## Relevant files

Expected to create or edit:

- `<file or area>`
- `<file or area>`

This list is guidance rather than a hard boundary in coding mode. Changes elsewhere require a coherent connection to the requested objective, not a verification failure or import error.

## Constraints

- Preserve the prototype warning and synthetic or properly de-identified data requirement.
- Validate before calculation or rule matching in completed executable clinical paths.
- Represent an unknown numeric value as `None`, never as zero.
- Do not silently infer required clinical context.
- Preserve fail-closed behavior for unsupported or insufficient clinical inputs.
- Keep clinical content inspectable and versioned.
- Preserve explicit units, assumptions, warnings, evidence, and provenance where applicable.

Temporary compilation errors, incomplete call sites, missing tests, failing tests, stale snapshots, lint diagnostics, and partially migrated code are permitted in coding mode. They must not be represented as verified or release-ready.

Delete any constraint above that is genuinely irrelevant only when doing so does not weaken a governing safety invariant.

## Verification

### Coding mode

Run checks when they improve implementation confidence or help diagnose the work. Verification is optional and non-blocking unless a check is explicitly included in the task's done condition.

Possible commands:

```bash
<targeted test, type check, lint command, smoke test, or none>
```

Report one of:

- checks run and their actual results;
- checks not run because they were unnecessary for this coding step; or
- checks skipped or blocked by the environment.

A failing or unavailable check does not require stopping coding-mode work. Do not weaken clinical safety behavior solely to make a check pass.

### Hardening mode

Define the exact regressions or verification debt to resolve. Run the checks needed to demonstrate the requested hardening objective. Full-suite execution is appropriate when shared behavior or public contracts are being reconciled.

### Release or checkpoint verification

Include this subsection only when verifying a release candidate, checkpoint, or milestone.

Before running checks, record:

```bash
git rev-parse HEAD
git status --short
python --version
python -m pytest --version
python -m ruff --version
python -m ruff check . --config pyproject.toml --show-settings
```

Also record the repository root, operating system, architecture, verification timestamp with UTC
offset, and release custodian.

The durable artifact must contain each exact command line before its output and must record the real
exit status, timestamps, counts, warnings, and evidence location for:

```bash
python -m pytest -q
python -m ruff check . --config pyproject.toml
PYTHONPATH=src python examples/cli_walkthrough.py --verify
```

Requirements:

- The candidate tree is clean before verification.
- Every skip, xfail, and xpass has an explicit disposition.
- The CLI output and exit status are retained.
- A pipeline such as `tee` must not hide a failing command status.
- Evidence generated after verification is distinguished from candidate files.
- Any later change to code, tests, snapshots, goldens, content, configuration, or verification tooling invalidates the candidate and requires a new exact commit.
- Do not weaken tests, delete required fixtures, overwrite snapshots, regenerate goldens, or add broad suppressions solely to produce a release pass.

For a failed Day 83 release gate, follow [`docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md`](PROTOTYPE_RELEASE_REMEDIATION_PLAN.md) when that plan remains applicable.

## Close procedure

1. Summarize the files created, edited, and deleted.
2. Report verification honestly, including when it was not run or remains failing.
3. State unresolved implementation limitations that materially affect subsequent work.
4. Update the designated active-state note by replacing stale status rather than appending a running diary.
5. Record the next coherent development action when useful.
6. Do not describe coding-mode output as a verified release candidate.
