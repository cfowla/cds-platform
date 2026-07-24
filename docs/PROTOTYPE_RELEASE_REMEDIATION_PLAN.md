# Prototype Release Remediation Plan

> **Prototype only — not for direct clinical use.** Use only synthetic or properly de-identified
> data. This plan repairs software verification and evidence quality; it does not authorize clinical
> use, change clinical-content review status, or expand the frozen renal-dosing scope.

## Status and baseline

The Day 83 prototype milestone remains a release `no-go`.

- Tested software candidate: `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0`
- Verification runtime: Python 3.12.1
- Durable evidence:
  `artifacts/verification/full-verification-20260724T082921Z.txt`
- Pytest: 63 failed, 869 passed, 16 skipped; exit status 1
- Ruff: 284 diagnostics, 261 reported fixable; exit status 1
- CLI walkthrough: not recorded
- Evidence-only PR: #53
- Evidence merge commit: `196a351eb48b30a70616d862a640190e0201c9e6`

PR #53 changed no implementation or tests. The tested software state remains the pre-merge candidate
listed above. Every remediation change invalidates that candidate for release purposes.

## Governing rules

- Preserve validation requirements. Repair stale test inputs rather than weakening the validator.
- Do not delete a required synthetic fixture, overwrite a snapshot, or regenerate a golden solely to
  obtain a pass.
- Do not use repository-wide Ruff automatic fixes until the intended ruleset is explicit.
- Keep each work package bounded and verify it before moving to the next package.
- Do not combine the known body-weight-type or famotidine minimum-weight implementation gaps with the
  fixture repair. Their strict xfails must first be restored as trustworthy signals.
- Any code, test, snapshot, golden, content, or verification-tooling change requires selection and
  verification of a new exact candidate commit.

## Root-cause map

| Area | Current evidence | Primary files | Required outcome |
| --- | --- | --- | --- |
| Integration fixtures | 57 listed failures stop at missing route and indication systems | `tests/integration/test_renal_dose_matrix.py`; `tests/integration/test_renal_safety_invariants.py` | Full-flow tests reach their intended calculation, repository, rule, failure, and provenance stages |
| Strict xfails | Weight-type conflict and famotidine minimum-weight cases XPASS for the wrong reason | `tests/integration/test_renal_dose_matrix.py` | Both cases are strict XFAIL after fixture repair unless separately fixed with direct evidence |
| Content snapshot | Synthetic cefepime fixture is present but absent from the hard-coded review snapshot | `tests/contract/test_renal_content_snapshots.py`; `src/cds/content/renal/cefepime_synthetic_fixture.yaml` | Explicit snapshot scope is documented and the focused contract test passes |
| Cefepime golden | Canonical regeneration has a one-byte case difference | `tests/unit/rules/test_cefepime_golden_cases.py`; committed cefepime golden JSON; shared exact matcher | Semantic diff is reviewed before any golden replacement |
| Decimal context | Two failures use ineffective `Context` object equality | `tests/unit/services/test_renal.py` | Relevant global-context properties are unchanged after calculation |
| Ruff | Artifact reports broad rule families without the exact command or effective settings | `pyproject.toml`; files named by the configured rerun | Intended ruleset is explicit; only its diagnostics are resolved or narrowly suppressed |
| Evidence record | Commands, tool versions, OS/architecture, clean-tree status, CLI result, and skip disposition are incomplete | release verification procedure and durable artifact | A new evidence artifact satisfies every checklist-required fact |

## Work package 1 — Repair stale integration order fixtures

### Scope

Edit only:

- `tests/integration/test_renal_dose_matrix.py`
- `tests/integration/test_renal_safety_invariants.py`
- `CURRENT.md` at task close

In each `_order()` helper, supply explicit synthetic coding systems for:

- `order.route.system`; and
- `order.indication.system`.

Use stable test-only constants and preserve the exact route and indication codes already derived from
the selected content. Do not change `src/cds/validation/medication.py`.

### Verification

```bash
python -m pytest tests/integration/test_renal_dose_matrix.py \
  tests/integration/test_renal_safety_invariants.py -q
```

### Acceptance gate

- No failure reports `missing_required_route_system` or
  `missing_required_indication_system` for a valid fixture.
- Full-flow success cases reach calculation, content lookup, rule matching, recommendation, and
  provenance assertions.
- Failure-injection cases reach the stage they are intended to test.
- `test_declared_weight_type_conflict_fails_closed` is strict XFAIL, not XPASS.
- `UNSUP-FAM-WEIGHT` is strict XFAIL, not XPASS.
- No implementation, content, snapshot, golden, or lint configuration changes are included.

Stop if a new failure shows that route or indication systems participate in a stricter exact-match
contract than the current fixtures express. Inspect only the directly relevant matcher or content
schema before deciding the next bounded change.

## Work package 2 — Resolve the renal-content snapshot scope

### Decision

Choose and document one policy:

1. **Directory-complete snapshot:** every YAML document under `src/cds/content/renal` is part of the
   review snapshot, including synthetic, draft, and ineligible fixtures; or
2. **Explicit selected-content snapshot:** the contract test names the clinical-content documents it
   reviews, while synthetic fixtures are verified by separate schema and eligibility tests.

The second policy usually produces a clearer clinical review boundary, but the repository decision
must be based on the contract test's stated purpose and existing conventions rather than convenience.

### Scope

Inspect and edit only what the decision requires:

- `tests/contract/test_renal_content_snapshots.py`
- `src/cds/content/renal/cefepime_synthetic_fixture.yaml` only for inspection unless the fixture is
  independently shown to be obsolete or defective
- the directly relevant content-schema or fixture test if needed to preserve synthetic-fixture
  coverage

### Verification

```bash
python -m pytest tests/contract/test_renal_content_snapshots.py -q
```

Also run the focused test that proves the synthetic fixture remains draft, ineligible, and valid for
its intended test purpose.

### Acceptance gate

- Snapshot scope is explicit in test names, comments, or helper structure.
- The synthetic fixture is not deleted merely to make the snapshot pass.
- Draft and synthetic status does not become eligible for recommendation matching.
- The contract test produces an inspectable diff for future selected-content changes.

## Work package 3 — Review the cefepime golden semantic diff

### Scope

Inspect:

- `tests/unit/rules/test_cefepime_golden_cases.py`
- the committed cefepime golden JSON files used by that test
- the canonical regeneration helper
- the shared exact matcher and the cefepime rule only as needed to explain the changed byte

Do not overwrite the golden before identifying the exact field and semantic meaning of the
lowercase-versus-uppercase difference.

### Review questions

- Is the changed value a clinician-facing display string, a coded identifier, an enum wire value, or
  serialization-only formatting?
- Did the shared matcher intentionally standardize this field?
- Does the changed output preserve exact identifiers and existing public serialization contracts?
- Would accepting the change weaken reviewability or silently normalize case-sensitive content?

### Verification

Run the existing focused golden test before and after the approved change:

```bash
python -m pytest tests/unit/rules/test_cefepime_golden_cases.py -q
```

### Acceptance gate

- The semantic difference is recorded in the task summary or pull-request description.
- If the generated output is wrong, fix the rule or serializer and keep the reviewed golden.
- If the generated output is intended, regenerate only the affected golden files and review their
  complete diff.
- No unrelated golden files are rewritten.

## Work package 4 — Correct the Decimal-context preservation assertions

### Scope

Edit only the focused tests in `tests/unit/services/test_renal.py` unless a direct test failure proves
that calculator code actually mutates the global context.

Replace object equality with explicit value comparisons for at least:

- `prec`
- `rounding`
- `Emin`
- `Emax`
- `capitals`
- `clamp`
- `traps`
- `flags`

A small test helper may serialize these properties into a tuple or dictionary before and after the
calculation. Preserve flags and traps; do not clear or ignore them merely to pass the test.

### Verification

```bash
python -m pytest tests/unit/services/test_renal.py -q
```

### Acceptance gate

- Both extreme-creatinine parameter cases pass.
- The test still proves the supplied finite positive Decimal is used exactly.
- The test proves the caller's global Decimal context configuration, traps, and flags are unchanged.
- No calculator behavior is changed unless the property comparison reveals a real mutation.

## Work package 5 — Establish and remediate the Ruff baseline

### Capture the effective configuration first

From a clean repository root, record exact commands and versions:

```bash
python -m ruff --version
python -m ruff check . --config pyproject.toml --show-settings \
  > artifacts/verification/ruff-settings.txt
python -m ruff check . --config pyproject.toml 2>&1 \
  | tee artifacts/verification/ruff-results-rerun.txt
```

Record the Ruff command's actual exit status without allowing the `tee` pipeline to hide it. Use an
appropriate shell mechanism such as `pipefail` or capture the command status separately.

### Classify before editing

Group configured diagnostics into:

- definite defects or dead code, such as unused imports;
- safe mechanical style changes under the selected ruleset;
- intentional negative-test constructions;
- diagnostics requiring a policy decision; and
- diagnostics outside the repository's intended ruleset.

### Constraints

- Do not use repository-wide `--fix`.
- Do not use `--unsafe-fixes`.
- Do not add broad file-level ignores when a line-level suppression documents the intentional case.
- Do not add timezones to datetime values whose purpose is to prove that naive input is rejected.
- Do not replace exact Decimal string construction when the string form is intentional for
  reproducibility or audit semantics without first confirming equivalent behavior.
- Do not change exception boundaries or safety behavior solely to satisfy stylistic diagnostics.

### Acceptance gate

- `pyproject.toml` or the documented command makes the intended ruleset reproducible.
- All remaining diagnostics under that ruleset are either fixed or narrowly suppressed with a reason.
- `python -m ruff check . --config pyproject.toml` exits 0.
- Focused tests for any behavior-bearing lint edits pass.

## Work package 6 — Resolve placeholder skips and repair evidence capture

### Placeholder skips

The recorded 16 skips are placeholder tests. For each placeholder:

- replace it with an implemented test when the component behavior now exists;
- remove it when it is redundant and its intended coverage is already present; or
- record an explicit release-custodian acceptance with the exact file, reason, and nonclinical
  prototype impact.

Do not count a skip as a pass. Do not replace a skip with a trivial assertion.

### Required environment record

Before running release verification, record:

```bash
git rev-parse HEAD
git status --short
python --version
python -m pytest --version
python -m ruff --version
```

Also record operating system, architecture, verification timestamp with UTC offset, repository root,
and the release custodian. The working tree must be clean before candidate verification begins.

### Required command record

The durable artifact must contain the exact command line before each command's output, including:

```bash
python -m pytest -q
python -m ruff check . --config pyproject.toml
PYTHONPATH=src python examples/cli_walkthrough.py --verify
```

For each command, record start time, completion time, exit status, counts, warnings, and durable
artifact location. Record all skips, xfails, and xpasses with explicit disposition.

Generated evidence files may make the working tree dirty after verification. Record the clean state
before the first check and distinguish generated evidence from candidate files. Commit evidence only
after it has been reviewed for PHI and accuracy.

### Acceptance gate

- Every release-checklist evidence field is populated or explicitly blocking.
- The CLI output includes `7 synthetic CLI walkthrough scenarios verified.` and exit status 0.
- No real patient identifiers or clinical payloads appear in retained evidence.
- The evidence artifact names the exact unchanged candidate commit.

## Work package 7 — Select and verify a new candidate

Only after work packages 1-6 are complete:

1. Commit all intended repairs.
2. Confirm the working tree is clean.
3. Record the new exact candidate SHA.
4. Run the full verification commands with the repaired evidence procedure.
5. Review every failure, skip, warning, xfail, and xpass.
6. Complete independent calculation review for the exact new candidate.
7. Complete qualified independent clinical-content review for every selected exact content version.
8. Complete PHI review and limitation dispositions.
9. Record an explicit `go` or `no-go` in `docs/PROTOTYPE_RELEASE_CHECKLIST.md`.
10. Create a prototype milestone tag only in a separate bounded task and only after an explicit `go`.

### Final software gate

```bash
python -m pytest -q
python -m ruff check . --config pyproject.toml
PYTHONPATH=src python examples/cli_walkthrough.py --verify
```

Required software outcome:

- pytest exit status 0 with every skip and expected failure explicitly accepted;
- Ruff exit status 0 under the recorded effective configuration;
- CLI walkthrough exit status 0 with all seven scenarios verified;
- no test weakened, deleted, reclassified, snapshot-overwritten, or golden-regenerated solely to
  obtain a pass; and
- all evidence tied to one exact unchanged commit.

Passing software verification is necessary but not sufficient for a release `go`. The independent
calculation, clinical-content, PHI, limitation, and custodian gates in
`docs/PROTOTYPE_RELEASE_CHECKLIST.md` remain mandatory.

## Work-package sequence

Each line is one separate bounded task:

1. Repair integration route and indication systems; rerun two integration files.
2. Decide and implement renal-content snapshot scope; rerun focused contract coverage.
3. Review the cefepime semantic golden diff; fix output or approve targeted regeneration.
4. Replace invalid Decimal-context equality; rerun renal service tests.
5. Capture Ruff settings; select ruleset; remediate only configured diagnostics.
6. Resolve placeholder skips and implement complete release-evidence capture.
7. Select a new clean candidate and rerun full pytest, Ruff, and CLI verification.
8. Complete independent reviews and make a new explicit release decision.
