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
- PR #55 merged the bounded integration fixture repair. Its merge commit is
  `1bd7bc2a6976734b2ec74832bdb48db1bbd19322`.
- The tested Day 83 candidate failed software verification and remains a release `no-go`.
- The route and indication fixture blocker is resolved.
- The newly exposed renal-value Decimal textual mismatch now has an implemented contract decision,
  but the repository-focused pytest acceptance command has not been executed in a complete checkout.

## Current state

The durable Day 83 evidence remains:

`artifacts/verification/full-verification-20260724T082921Z.txt`

Recorded results for candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0`:

- Pytest: 63 failed, 869 passed, 16 skipped; exit status 1.
- Ruff: 284 diagnostics, 261 reported fixable; exit status 1.
- CLI walkthrough: not recorded in the artifact.
- Working tree: ended with untracked `artifacts/` because the evidence file was being created.

The focused integration run after the fixture repair reached the intended calculation, exact content
lookup, rule matching, recommendation, and provenance stages. Its remaining 39 failures were textual:
calculated values such as `11.0`, `10.99990`, and `60.00010` compared numerically equal to the target
but differed from the canonical strings `11`, `10.9999`, and `60.0001` expected by the integration
matrix.

The renal-value textual contract is now defined as follows:

- The Cockcroft-Gault numeric result remains an unrounded `Decimal` calculated at the existing local
  precision and rounding context.
- Calculated renal values use canonical non-exponent plain-decimal representation.
- Only fractional trailing zeros introduced by arithmetic scale are removed.
- No binary floating-point conversion, quantization, clinical rounding, unit conversion, or boundary
  normalization is permitted.
- The canonical `Decimal` is stored in `RenalFunctionResult`; the shared exact matcher and generic JSON
  serializer therefore emit the same canonical string without special-case formatting.
- Generic serialization still preserves the scale of other supplied `Decimal` values. This change is
  limited to the representation deliberately selected by the Cockcroft-Gault calculator.

Implementation:

- `src/cds/services/renal.py` now canonicalizes the completed unrounded calculation by formatting it as
  non-exponent decimal text and removing fractional trailing zeros before reconstructing the same
  numeric `Decimal` value.
- No rule, serializer, content, snapshot, golden, validation, interface, or lint configuration changed.

Verification limitation:

- The execution environment had Python 3.13.5 and pytest 9.0.2 available.
- No repository checkout was supplied.
- The exact focused repository pytest command was not executed because the GitHub connector does not
  expose a runnable checkout and substitute functional test runners are prohibited.
- A direct Decimal diagnostic confirmed that the known fixture arithmetic representations
  `11.0`, `10.99990`, `20.0`, `59.99990`, and `60.00010` become `11`, `10.9999`, `20`, `59.9999`, and
  `60.0001` without changing numeric equality. This diagnostic is not a replacement for repository
  pytest verification.

## Remaining repair areas

1. Run the two affected integration files in a complete checkout and confirm the 39 textual failures
   are resolved without changing band selection or strict-XFAIL behavior.
2. Resolve the synthetic-content snapshot policy intentionally and rerun its contract test.
3. Inspect the semantic cefepime golden diff, then regenerate only if the changed canonical output is
   approved.
4. Replace invalid `Context == Context.copy()` assertions with property-by-property comparisons and
   rerun the focused renal service tests.
5. Capture Ruff effective settings, establish the intended ruleset, then fix or narrowly suppress only
   diagnostics produced by that configuration.
6. Explicitly resolve or accept the 16 placeholder skips and repair the verification evidence procedure
   so every required command, version, environment fact, exit status, and CLI result is durable.
7. Create a new candidate commit and rerun full pytest, configured Ruff, and the seven-scenario
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
- Do not place patient identifiers, clinical payloads, exception messages, or tracebacks in diagnostic
  logs or CLI diagnostics.
- Do not weaken a safety test, delete a fixture, overwrite a snapshot, regenerate a golden, or alter
  lint configuration solely to obtain a passing result.
- Do not create a prototype tag unless the release checklist has an explicit `go` decision for the
  exact unchanged candidate commit and selected content versions.

## Blockers

- Candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` failed pytest and Ruff verification.
- The canonical renal-value change has not yet passed the required focused integration command in a
  complete checkout.
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
- Conflicting supplied versus declared body-weight type is not currently rejected before calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The logging policy is not yet wired into application or interface failure paths.

These blockers prevent an honest `go`, changelog update, or prototype milestone tag.

## Files changed

- `src/cds/services/renal.py` - defines and applies canonical non-exponent representation for calculated
  Cockcroft-Gault values without rounding or float conversion.
- `CURRENT.md` - records the contract decision, implementation, verification limitation, remaining
  acceptance command, and next bounded action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded-task, targeted-verification, and close-procedure requirements.
- `docs/SAFETY_INVARIANTS.md` - exact Decimal, auditability, pure-service, and fail-closed constraints.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - release no-go context and ordered repair work packages.
- `tests/integration/test_renal_dose_matrix.py` - exact boundary, audit-string, serialization, and
  strict-XFAIL assertions.
- `tests/unit/services/test_renal.py` - unrounded calculation and caller-context expectations.
- `tests/unit/utils/test_serialization.py` - generic Decimal precision-and-scale serialization contract.
- `src/cds/rules/exact_renal_dose.py` - confirms audit data records `str(renal_value)` from the calculated
  result.
- `src/cds/utils/serialization.py` - confirms response-boundary Decimal values serialize with `str()`.

## Next exact action

> In a complete development checkout of the exact merged commit, run:
>
> ```bash
> python -m pytest tests/integration/test_renal_dose_matrix.py \
>   tests/integration/test_renal_safety_invariants.py -q
> ```
>
> Confirm that all prior `renal_value` textual failures are gone, all boundary band identifiers remain
> unchanged, `test_declared_weight_type_conflict_fails_closed` remains strict XFAIL, and
> `UNSUP-FAM-WEIGHT` remains strict XFAIL. If this acceptance gate passes, begin the separate bounded
> synthetic-content snapshot policy task. If it fails, inspect only the directly reported renal
> calculation, exact matcher, serializer, or focused assertion before making another change.
