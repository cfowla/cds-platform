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
  `no-go`; this bounded golden reconciliation does not certify a new release candidate.
- **INT-2 renal integration acceptance remains complete.**
- **Work Package 2 renal-content snapshot scope remains complete.**
- **Work Package 3 cefepime golden semantic review and follow-up reconciliation are complete.**
- **Work Package 4 Decimal-context assertion correction and focused verification are complete.**
- **Work Package 5 Ruff-baseline selection and remediation are complete.**

## Cefepime golden follow-up result

Implemented from current `main` base commit
`f8e5a754df1470be5f4de0907af532763e09f9a2`.

Exact remaining mismatch:

- The prior semantic-review task correctly updated the three successful-case goldens from lowercase
  `cefepime` to display-form `Cefepime`.
- Supplemental full-suite verification still failed because
  `unstable_renal_function.json` retained the earlier medication-specific sentence:
  `Unstable renal function is outside the supplied reviewed cefepime content context.`
- The shared exact matcher now intentionally produces the medication-neutral sentence:
  `Unstable renal function is outside the supplied reviewed content context.`
- Canonical regeneration uses that sentence in both the top-level `RuleResult.summary` and the mirrored
  warning `message`.

Approved bounded change:

- Regenerated only
  `examples/golden/cefepime_rule/unstable_renal_function.json` from the current canonical output.
- Removed the stale lowercase medication name from exactly two human-readable fields.
- Preserved the result status, applied and passed states, warning code, identifiers, content version,
  regimen, renal value and unit, provenance, timestamps, and every other serialized field.
- Did not change production rules, serializer behavior, clinical content, test logic, other goldens,
  dependencies, lint configuration, or workflows.

## Verification

The focused test and its directly required import graph were materialized from current `main` in a
bounded connector-backed checkout. An isolated virtual environment installed the repository-declared
`.[dev]` dependencies from `pyproject.toml`.

Final targeted verification:

```bash
python -m pytest tests/unit/rules/test_cefepime_golden_cases.py -q
```

Result:

- Exit status: 0.
- 4 tests passed.
- Canonical byte matching, deterministic regeneration, required outcome coverage, and synthetic
  fail-closed assertions all passed.

The complete test suite was not rerun for this bounded task. This result does not select or certify a
release candidate.

## Remaining repair areas

1. **Work Package 6:** resolve the 16 placeholder skips and repair durable release-evidence capture.
2. **Work Package 7:** select and fully verify a new release candidate only after Work Package 6 is
   complete.
3. Complete the independent calculation, qualified content, PHI, release-custodian, and final decision
   reviews for one exact unchanged candidate.
4. Tag the prototype milestone only after an explicit `go` decision.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate before calculation or rule matching; unsupported or insufficient cases fail closed.
- Keep identifiers, coding systems, units, and case exact; do not infer, alias, convert, or normalize
  them.
- Preserve exact Decimal behavior and numeric-string serialization without binary floating-point
  conversion or clinical rounding.
- Preserve public imports, exception behavior, serialization contracts, clinical content, and safety
  boundaries unless a separate task explicitly authorizes a change.
- Preserve the caller's Decimal context configuration, traps, and flags.
- Do not weaken tests, remove fixtures, overwrite unrelated snapshots or goldens, alter XFAIL markers,
  or modify lint configuration merely to produce a pass.
- Do not create a prototype tag without an explicit `go` decision for one exact unchanged candidate
  and its selected content versions.

## Blockers

- Placeholder-skip dispositions, CLI evidence, clean candidate evidence, independent calculation
  approval, qualified content review, PHI review, release-custodian approval, and a final decision
  record remain incomplete.
- Existing known clinical and architecture limitations remain outside this task, including weight-type
  conflict handling, the famotidine adult minimum-weight boundary, content supersession, standalone CLI
  composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

- `examples/golden/cefepime_rule/unstable_renal_function.json` - reconciles the two stale
  human-readable strings with current canonical regeneration.
- `CURRENT.md` - records the semantic difference, focused verification, remaining blockers, and next
  exact action.

No production implementation, clinical content, test logic, serializer, other golden, snapshot,
dependency, workflow, lint configuration, or public contract changed.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded-task, verification, and close-procedure requirements.
- `docs/SAFETY_INVARIANTS.md` - exactness, auditability, synthetic-data, and safety constraints.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - golden-review scope and acceptance gate.
- `tests/unit/rules/test_cefepime_golden_cases.py` - canonical generator and focused assertions.
- `src/cds/rules/cefepime.py` - medication-specific matcher configuration.
- `src/cds/rules/exact_renal_dose.py` - source of the medication-neutral unstable-function summary.
- `src/cds/utils/serialization.py` - deterministic canonical JSON behavior.
- The seven committed cefepime golden files - confirmed only the unstable-function golden still
  differed from canonical regeneration.
- `project_sources/01-Architect-for-CDS.txt` - confirmed that shared rule matching remains simple,
  pure, deterministic, and separated from clinical content.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute Work Package 6 as a separate bounded task:
inventory and disposition the 16 placeholder skips, then implement complete durable release-evidence
capture without treating a skip as a pass or combining release-candidate selection.
