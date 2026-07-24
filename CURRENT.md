# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available, use
the GitHub connector to materialize only named files and concretely required imports in a bounded
verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:

- repository cloning or broad filesystem searches for another checkout;
- GitHub Actions or CI investigation;
- workflow creation or modification;
- broad repository review; and
- substitute functional test runners.

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1-82 are complete.
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The software candidate tested for Day 83 was
  `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` under Python 3.12.1.
- PR #53 merged only the durable verification artifact. Its merge commit is
  `196a351eb48b30a70616d862a640190e0201c9e6`; it did not change implementation or tests.
- PR #55 merged the bounded integration fixture repair to `main`. Its merge commit is
  `1bd7bc2a6976734b2ec74832bdb48db1bbd19322`.
- The tested Day 83 candidate failed software verification and remains a release `no-go`.
- Remediation work package 1 implementation is merged, but its focused acceptance gate is not yet
  satisfied because the two-file integration run remains red for a newly exposed Decimal-text
  mismatch.

## Current state

The durable Day 83 evidence remains:

`artifacts/verification/full-verification-20260724T082921Z.txt`

Recorded results for candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0`:

- Pytest: 63 failed, 869 passed, 16 skipped; exit status 1.
- Ruff: 284 diagnostics, 261 reported fixable; exit status 1.
- CLI walkthrough: not recorded in the artifact.
- Working tree: ended with untracked `artifacts/` because the evidence file was being created.

Remediation work package 1 fixture implementation is now merged:

- `tests/integration/test_renal_dose_matrix.py` defines stable synthetic route and indication coding
  systems and supplies them in `_order()`.
- `tests/integration/test_renal_safety_invariants.py` defines the same stable synthetic systems and
  supplies them in `_order()`.
- Existing route and indication codes derived from selected content remain unchanged.
- No validator, implementation, content, snapshot, golden, or lint configuration changed in PR #55.

Focused verification was attempted with the required command:

```bash
python -m pytest tests/integration/test_renal_dose_matrix.py \
  tests/integration/test_renal_safety_invariants.py -q
```

Observed result in the bounded verification environment under Python 3.13.5 and pytest 9.0.2:

- 39 failed, 78 passed, 2 xfailed; exit status 1.
- No failure output contained `missing_required_route_system` or
  `missing_required_indication_system`.
- Full-flow cases reached calculation, exact content lookup, rule matching, recommendation, and
  provenance assertions before failing at the textual `renal_value` assertion.
- Failure-injection cases reached their intended stages and passed.
- `test_declared_weight_type_conflict_fails_closed` was strict XFAIL, not XPASS.
- `UNSUP-FAM-WEIGHT` was strict XFAIL, not XPASS.

All 39 failures had the same shape:

- the calculated `Decimal` compared numerically equal to the target;
- `supporting_data["renal_band_id"]` matched the expected band; but
- `supporting_data["renal_value"]` preserved arithmetic scale, such as `11.0`, `10.99990`, or
  `60.00010`, while the test expected `11`, `10.9999`, or `60.0001` from `str(target)`.

The current implementation constructs the calculated value without rounding and the shared exact
matcher records `str(renal_value)`. The next task must decide whether the audit string is intended to
preserve Decimal scale or use a canonical non-exponent textual form before changing either production
code or the test assertion.

Verification limitation:

- No complete supplied repository checkout was available.
- The GitHub connector was used to build a bounded checkout from the named tests, directly required
  imports, and referenced renal content.
- The bounded checkout is diagnostic evidence, not a hash-verified release-candidate checkout or a
  replacement for the durable Day 83 evidence artifact.
- The Decimal-text mismatch must be reproduced in a complete checkout before it is treated as a
  release-candidate result or fixed.

The remaining known repair areas are:

1. **Renal-value Decimal text contract.** Reproduce the 39 focused boundary failures in a complete
   checkout, decide the intended audit-string contract, and make the smallest code-or-test change that
   preserves unrounded Decimal matching and exact JSON numeric-string requirements.
2. **Stale content review snapshot.** The contract snapshot does not include
   `cefepime_synthetic_fixture.yaml`. The repository must deliberately decide whether the review
   snapshot includes every renal YAML document or only an explicit selected clinical-content set.
3. **Stale cefepime golden JSON.** Canonical regeneration differs from the committed golden at one
   reported byte after the cefepime rule was refactored to the shared exact matcher. The semantic
   difference must be reviewed before any golden regeneration.
4. **Invalid Decimal-context assertions.** Two unit failures compare `decimal.Context` objects with
   `==`. Relevant context properties must be compared individually.
5. **Ruff baseline and release evidence.** The intended Ruff ruleset, complete command evidence, CLI
   walkthrough, placeholder-skip dispositions, and release-review approvals remain unresolved.

## Active remediation plan

The controlling plan is
[`docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md`](docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md).
Continue as separate bounded tasks in this order:

1. **Implemented and merged; acceptance blocked:** explicit route and indication coding systems are
   present in both integration `_order()` helpers. The missing-system failure family is no longer the
   observed focused blocker, and both strict xfails are restored as XFAIL.
2. Reproduce and resolve the newly exposed `supporting_data["renal_value"]` Decimal textual-contract
   mismatch without rounding the calculated value or weakening boundary assertions.
3. Resolve the synthetic-content snapshot policy intentionally and rerun its contract test.
4. Inspect the semantic cefepime golden diff, then regenerate only if the changed canonical output is
   approved.
5. Replace `Context == Context.copy()` with property-by-property assertions and rerun the focused
   renal service tests.
6. Capture Ruff effective settings, establish the intended ruleset, then fix or narrowly suppress
   only diagnostics produced by that configuration. Do not run a repository-wide automatic fix.
7. Explicitly resolve or accept the 16 placeholder skips and repair the verification evidence
   procedure so every required command, version, environment fact, exit status, and CLI result is
   durable.
8. Create a new candidate commit and rerun full pytest, configured Ruff, and the seven-scenario
   synthetic CLI walkthrough from a clean tree.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Draft and retired clinical content are not eligible for a dosing recommendation.
- A reviewed status requires complete reviewer metadata for the exact content version.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers and units exact and case-sensitive; do not normalize, infer, alias, convert, or
  fall back.
- JSON clinical numerics remain strings at request boundaries and exact Decimal strings at response
  boundaries; do not convert them through binary floating point.
- Missing numerics remain `None`; missing enum categories use explicit `UNKNOWN` members.
- Datetimes crossing mapper and interface boundaries must include a usable UTC offset and serialize
  in UTC; do not assign a timezone to naive input.
- Keep domain models passive, services and rules pure, repositories responsible for content access,
  app modules responsible for orchestration, and mappers and interfaces free of clinical logic.
- Preserve existing public imports and serialized contracts unless a task explicitly changes them.
- Preserve unrounded calculated values for matching and auditability.
- Do not place patient identifiers, clinical payloads, exception messages, or tracebacks in
  diagnostic logs or CLI diagnostics.
- Do not weaken a safety test, delete a fixture, overwrite a snapshot, regenerate a golden, or alter
  lint configuration solely to obtain a passing result.
- Do not create a prototype tag unless the release checklist has an explicit `go` decision for the
  exact unchanged candidate commit and selected content versions.

## Blockers

- Candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` failed pytest and Ruff verification.
- The focused integration suite remains red with 39 Decimal textual-representation failures in the
  bounded verification run.
- The Decimal textual-contract finding has not yet been reproduced in a complete hash-verified
  checkout.
- The renal-content snapshot policy is unresolved for synthetic fixtures.
- The cefepime golden semantic change has not been reviewed.
- The Decimal-context tests contain an invalid equality assertion.
- The intended Ruff ruleset and effective configuration have not been established.
- The CLI walkthrough was not recorded.
- The 16 placeholder skips have no accepted release disposition.
- Required environment, command, version, clean-tree, and exit-status evidence is incomplete.
- Independent calculation approval is not recorded for an exact passing candidate.
- Independent clinical-content review is not recorded for every selected exact content version.
- A named qualified independent clinical-content reviewer remains unavailable.
- PHI review, limitation dispositions, release custodian approval, and the final decision record are
  incomplete.
- The current schema has no explicit supersession relationship or automatic active-version registry.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The logging policy is not yet wired into application or interface failure paths.

These blockers prevent an honest `go`, changelog update, or prototype milestone tag.

## Files changed

- `CURRENT.md` - replaces the stale pending-verification state with the merged fixture status, focused
  run outcome, newly exposed Decimal textual-contract blocker, verification limitation, and exact
  next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded-task, verification, and close-procedure requirements.
- `docs/SAFETY_INVARIANTS.md` - validation-before-computation, exact Decimal, and fail-closed
  constraints.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - work package 1 scope and acceptance gate.
- `tests/integration/test_renal_dose_matrix.py` - focused full-flow, failure-injection, boundary, and
  strict-XFAIL assertions.
- `tests/integration/test_renal_safety_invariants.py` - renal-band uniqueness, critical-stop, evidence,
  and provenance assertions.
- `src/cds/services/renal.py` - confirms the calculated Decimal remains unrounded and can retain
  arithmetic scale.
- `src/cds/rules/exact_renal_dose.py` - confirms supporting data currently records
  `str(renal_value)`.
- Directly required domain, validation, repository, rule, serialization, and renal YAML files were
  materialized only to collect and execute the focused tests in the bounded checkout.

## Next exact action

> In a complete development checkout of current `main`, reproduce one integer and one fractional
> boundary failure first:
>
> ```bash
> python -m pytest \
>   tests/integration/test_renal_dose_matrix.py::test_full_flow_boundaries \
>   -q -k 'BND-CEF-Q8-11-at or BND-CEF-Q8-11-below'
> ```
>
> If the mismatch reproduces, inspect only `src/cds/services/renal.py`,
> `src/cds/rules/exact_renal_dose.py`, `src/cds/utils/serialization.py`, and the focused assertion in
> `tests/integration/test_renal_dose_matrix.py`. Define whether `supporting_data["renal_value"]` must
> preserve Decimal scale or use a canonical non-exponent string, then make the smallest coherent
> code-or-test change. Preserve the unrounded Decimal used for band matching, do not convert through
> `float`, and rerun both affected integration files. Do not proceed to snapshot, golden, Ruff, or
> unrelated fixes in that task.
