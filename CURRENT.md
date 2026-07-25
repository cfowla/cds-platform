# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use a complete repository checkout supplied by a Codespace, local development environment, or
repository-connected Codex task. GitHub is authoritative. A repository-local or temporary isolated
virtual environment may be created, and project-declared development dependencies may be installed from
`pyproject.toml`. Do not install dependencies globally or reconstruct an incomplete checkout as
acceptance evidence.

## Roadmap position

- Days 1-82 are complete.
- **Day 83 - Tag the prototype milestone** remains incomplete.
- The original Day 83 candidate `73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` remains a release
  `no-go`; this bounded golden review does not certify a new release candidate.
- **INT-2 renal integration acceptance remains complete.**
- **Work Package 2 renal-content snapshot scope remains complete.**
- **Work Package 3 cefepime golden semantic review is complete.**

## Work Package 3 result

Reviewed from current `main` base commit `c69248686885307497c0342f136dfc9a7d5f66b9`.

Exact semantic difference:

- Field: top-level `RuleResult.summary` for the successful `normal`, `impaired`, and
  `exact_boundary` cefepime golden cases.
- Committed text: `Exact reviewed cefepime content matched one renal band.`
- Canonical generated text: `Exact reviewed Cefepime content matched one renal band.`
- The difference is one ASCII character per affected file: lowercase `c` versus uppercase `C`.

Classification and decision:

- The changed value is a clinician-facing display summary, not a coded identifier, enum wire value,
  renal unit, dose value, boundary value, or serialization-only numeric format.
- The shared exact matcher deliberately builds the sentence from
  `ExactRenalDoseRuleConfig.medication_display`.
- The cefepime rule explicitly configures that display value as `Cefepime`.
- The generated uppercase display is therefore the intended canonical output.
- Accepting it does not normalize or change the exact medication identifier `cefepime`, the `mL/min`
  unit, content identifiers, regimen identifiers, warning codes, renal bands, dose values, or safety
  behavior.

Approved bounded change:

- Updated only `examples/golden/cefepime_rule/normal.json`.
- Updated only `examples/golden/cefepime_rule/impaired.json`.
- Updated only `examples/golden/cefepime_rule/exact_boundary.json`.
- Each affected golden changes only the reviewed top-level summary character.
- The four fail-closed or unsupported goldens were inspected and did not require replacement.

## Verification

Required focused command:

```bash
python -m pytest tests/unit/rules/test_cefepime_golden_cases.py -q
```

Executable result:

- Not run in this connector session because no runnable repository checkout or active project virtual
  environment was supplied.
- A temporary branch-only GitHub Actions workflow was attempted, but GitHub exposed no workflow run or
  commit status for the head commit. The temporary workflow was removed and is absent from the final
  diff.
- Do not treat this task as release-candidate verification or claim pytest passed.

Static repository verification:

- GitHub comparison against `main` showed exactly the three intended golden files before this state-note
  update.
- Each golden reported one line added and one line deleted because the canonical JSON is stored on one
  line.
- Complete content review confirmed that the only semantic replacement in each affected file is
  `cefepime` to `Cefepime` in the top-level result summary.

## Remaining repair areas

1. **Work Package 4:** correct the Decimal-context preservation assertions in the focused renal service
   tests.
2. Establish and remediate the intended Ruff baseline without repository-wide automatic fixes.
3. Resolve placeholder skips and repair durable release-evidence capture.
4. Select and fully verify a new release candidate only after the preceding work packages are complete.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate before calculation or rule matching; unsupported or insufficient cases fail closed.
- Keep identifiers, coding systems, units, and case exact; do not infer, alias, convert, or normalize them.
- Preserve exact Decimal behavior and numeric-string serialization without binary floating-point
  conversion or clinical rounding.
- Preserve public imports, exception behavior, serialization contracts, clinical content, and safety
  boundaries unless a separate task explicitly authorizes a change.
- Do not weaken tests, remove fixtures, overwrite unrelated snapshots or goldens, alter XFAIL markers, or
  modify lint configuration merely to produce a pass.
- Do not create a prototype tag without an explicit `go` decision for one exact unchanged candidate and
  its selected content versions.

## Blockers

- The focused cefepime golden pytest command still requires execution in a complete checkout.
- Decimal-context tests contain invalid object-equality assertions.
- The intended Ruff ruleset and effective configuration remain unresolved.
- Placeholder-skip dispositions, CLI evidence, clean candidate evidence, independent calculation
  approval, qualified content review, PHI review, release-custodian approval, and a final decision record
  remain incomplete.
- Existing known clinical and architecture limitations remain outside this task, including weight-type
  conflict handling, the famotidine adult minimum-weight boundary, content supersession, standalone CLI
  composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

- `examples/golden/cefepime_rule/normal.json` - accepts the configured `Cefepime` display in the successful
  result summary.
- `examples/golden/cefepime_rule/impaired.json` - accepts the configured `Cefepime` display in the
  successful result summary.
- `examples/golden/cefepime_rule/exact_boundary.json` - accepts the configured `Cefepime` display in the
  successful result summary.
- `CURRENT.md` - records the exact semantic review, approved scope, verification limitation, and next
  bounded work package.

No production rule, serializer, clinical YAML, validation behavior, public identifier, unit, numeric
value, boundary, warning code, test logic, lint configuration, or workflow file remains changed.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded-task, targeted-verification, and close-procedure requirements.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - Work Package 3 scope, review questions, and acceptance
  gate.
- `tests/unit/rules/test_cefepime_golden_cases.py` - canonical case builder, byte-match test, and affected
  successful cases.
- `src/cds/rules/cefepime.py` - confirms the configured medication display is `Cefepime`.
- `src/cds/rules/exact_renal_dose.py` - confirms the successful summary uses the configured medication
  display without identifier normalization.
- The seven committed cefepime golden JSON files - identified the three affected successful cases and
  confirmed the other four require no change.
- `pyproject.toml` - confirmed the declared focused pytest environment and development dependencies.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute a separate bounded task for **Work Package 4 —
Correct the Decimal-context preservation assertions**. Edit only the focused tests in
`tests/unit/services/test_renal.py` unless a direct failure proves the calculator mutates global context,
and run:

```bash
python -m pytest tests/unit/services/test_renal.py -q
```
