# CDS Task Template

Use this template for one bounded implementation task. Copy it into a new task, replace every placeholder, and remove sections that do not apply. Do not add project history merely to make the prompt look complete.

## Read first

Read only the files needed to understand and verify this task:

- [`docs/SAFETY_INVARIANTS.md`](SAFETY_INVARIANTS.md)
- `<active state or prior-note file>`
- `<directly relevant implementation file>`
- `<directly relevant test file>`

Treat the named repository files as authoritative. Do not reconstruct requirements from prior chat history.

Read [`PROJECT_CHARTER.md`](../PROJECT_CHARTER.md) when the task changes clinical scope, supported medications or populations, safety behavior, clinical content requirements, intended users, or interfaces. Read [`FIRST_VERTICAL_SLICE.md`](../FIRST_VERTICAL_SLICE.md) when the task changes the frozen renal feature contract.

Inspect an additional file only when it is necessary to resolve:

1. an import or public API used by the task;
2. a failing test or error encountered during the task; or
3. a directly relevant repository convention that is not defined in the files above.

Do not perform a broad repository review unless the task explicitly requires one.

## Execution context

- Use the repository checkout already supplied by the execution environment.
- Probe the current working directory once with `git rev-parse --show-toplevel`.
- Do not search the filesystem for another checkout and do not clone the repository.
- If no checkout is available, use the GitHub connector to materialize a bounded verification checkout at `/tmp/cds-platform`.
- Initially materialize only the `Read first` files, the focused tests, required ancestor `__init__.py` files, and `pyproject.toml` when needed.
- Expand that checkout only for imports or resources concretely required by focused test collection or execution.
- Preserve repository-relative paths and do not reconstruct the full repository.
- GitHub remains authoritative for source retrieval and final repository changes; the bounded checkout exists only for implementation and focused verification.

## One deliverable

Implement **`<one precise, coherent deliverable>`**.

Done when: `<one observable completion condition>`.

Do not combine this task with adjacent cleanup, future feature work, or speculative extensibility.

## Required behavior

- `<observable requirement 1>`
- `<observable requirement 2>`
- `<observable requirement 3>`

For CDS behavior, state how missing, invalid, unsupported, or indeterminate inputs must be represented. Do not rely on vague requirements such as “robust,” “safe,” or “production-ready” without executable acceptance criteria.

## Non-goals

- Do not `<adjacent task or feature>`.
- Do not redesign unrelated modules.
- Do not add dependencies unless this task has a documented need for one.
- Do not add future API, EHR, persistence, user-interface, or clinical-domain concerns.
- Do not silently expand the frozen renal vertical slice; record proposed expansion in `BACKLOG.md` instead.

## Relevant files

Expected to create:

- `<new file, or none>`

Expected to edit:

- `<implementation file>`
- `<test file>`

Do not edit:

- `<protected or unrelated file, if applicable>`

Changes outside this list require a direct explanation tied to an import, failure, or relevant convention.

## Constraints

- Preserve the prototype warning and synthetic or properly de-identified data requirement.
- Validate before calculation or rule matching.
- Represent an unknown numeric value as `None`, never as zero.
- Keep domain models free of service, validation, serialization, and I/O behavior.
- Keep calculators and rule evaluators pure and deterministic.
- Preserve explicit units, assumptions, warnings, evidence, and provenance where applicable.
- Prefer the smallest coherent change that satisfies the acceptance criteria.

Delete any constraint above that is genuinely irrelevant to the task rather than repeating it mechanically.

## Targeted verification

Run the narrowest command that proves the deliverable:

```bash
<targeted test or validation command>
```

Expected result: `<specific passing tests, output, or invariant>`.

Run the full suite only when the task changes shared behavior, public contracts, package structure, or when the task explicitly requires a checkpoint. Do not claim tests or CI passed unless they were actually run.

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
- Any later change to code, tests, snapshots, goldens, content, configuration, or verification
  tooling invalidates the candidate and requires a new exact commit.
- Do not weaken tests, delete required fixtures, overwrite snapshots, regenerate goldens, or add
  broad suppressions solely to produce a pass.

For a failed Day 83 release gate, follow
[`docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md`](PROTOTYPE_RELEASE_REMEDIATION_PLAN.md) and keep one work
package per task.

## Close procedure

1. Summarize the files created, edited, and deleted.
2. Report the exact verification command and result.
3. State any unresolved limitation or skipped verification honestly.
4. Update the designated active-state note by replacing stale status rather than appending a running diary.
5. Record one exact next action that can be completed as a separate bounded task.
6. Do not create a new dated checkpoint file unless explicitly requested.
