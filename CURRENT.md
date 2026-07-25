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
  `no-go`; this bounded test correction does not certify a new release candidate.
- **INT-2 renal integration acceptance remains complete.**
- **Work Package 2 renal-content snapshot scope remains complete.**
- **Work Package 3 cefepime golden semantic review remains complete.**
- **Work Package 4 Decimal-context assertion correction is implemented; focused repository verification
  remains pending.**

## Work Package 4 result

Implemented from current `main` base commit `f2e39ab97b4714fc01d2a2b28f30ba7453ef805a`.

Root cause:

- The two extreme-creatinine parameter cases copied the active Decimal `Context` and then compared the
  copied object to `getcontext()` with object equality.
- That assertion did not explicitly compare the context properties the test intended to preserve.
- The production calculator already confines precision and rounding changes inside `localcontext()`; no
  direct evidence showed that calculator code mutates the caller's global Decimal context.

Approved bounded change:

- Added `_decimal_context_state()` in `tests/unit/services/test_renal.py`.
- The helper snapshots `prec`, `rounding`, `Emin`, `Emax`, `capitals`, `clamp`, `traps`, and `flags` as
  directly comparable values.
- Replaced the ineffective `Context` object-equality assertion with an explicit before-and-after state
  comparison in both parameterized extreme-creatinine cases.
- Preserved the assertions that the supplied finite positive Decimal is used exactly and retains its
  original tuple representation.
- Did not change `src/cds/services/renal.py` or any clinical, validation, serialization, content, or
  public-contract behavior.

## Verification

Required focused command:

```bash
python -m pytest tests/unit/services/test_renal.py -q
```

Executable result:

- Not run against a complete repository checkout in this connector session.
- The supplied execution directory was probed once with `git rev-parse --show-toplevel` and was not a Git
  checkout.
- Python 3.13.5 and pytest 9.0.2 were available, but outbound repository download was unavailable and an
  incomplete reconstructed tree is not accepted as repository verification.
- Do not claim the focused pytest file passed.

Supplemental sanity check:

- A standalone Python check exercised the exact context-state fields across the two configured extreme
  creatinine values and confirmed that a `localcontext()` calculation left the caller context state
  unchanged.
- Result: `2 Decimal-context preservation cases passed`.
- This check supports the assertion design but is not a substitute for the required repository pytest
  command.

Static repository verification:

- GitHub comparison against `main` before this state-note update showed exactly one modified file:
  `tests/unit/services/test_renal.py`.
- The focused test diff contained 16 additions and 2 deletions: one small helper and the two assertion
  replacements.
- Complete focused review confirmed that no production calculator file was changed.

## Remaining repair areas

1. Execute the focused Work Package 4 pytest command in a complete checkout and record the real result.
2. **Work Package 5:** establish and remediate the intended Ruff baseline without repository-wide
   automatic fixes.
3. **Work Package 6:** resolve placeholder skips and repair durable release-evidence capture.
4. **Work Package 7:** select and fully verify a new release candidate only after the preceding work
   packages are complete.
5. Tag the prototype milestone only after an explicit `go` decision for one exact unchanged candidate.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate before calculation or rule matching; unsupported or insufficient cases fail closed.
- Keep identifiers, coding systems, units, and case exact; do not infer, alias, convert, or normalize them.
- Preserve exact Decimal behavior and numeric-string serialization without binary floating-point
  conversion or clinical rounding.
- Preserve public imports, exception behavior, serialization contracts, clinical content, and safety
  boundaries unless a separate task explicitly authorizes a change.
- Preserve the caller's Decimal context configuration, traps, and flags.
- Do not weaken tests, remove fixtures, overwrite unrelated snapshots or goldens, alter XFAIL markers, or
  modify lint configuration merely to produce a pass.
- Do not create a prototype tag without an explicit `go` decision for one exact unchanged candidate and
  its selected content versions.

## Blockers

- The focused Work Package 4 pytest command still requires execution in a complete checkout.
- The intended Ruff ruleset and effective configuration remain unresolved.
- Placeholder-skip dispositions, CLI evidence, clean candidate evidence, independent calculation
  approval, qualified content review, PHI review, release-custodian approval, and a final decision record
  remain incomplete.
- Existing known clinical and architecture limitations remain outside this task, including weight-type
  conflict handling, the famotidine adult minimum-weight boundary, content supersession, standalone CLI
  composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

- `tests/unit/services/test_renal.py` - replaces ineffective Decimal `Context` object equality with an
  explicit snapshot of all required caller-context properties.
- `CURRENT.md` - records the root cause, bounded change, verification limitation, and next exact action.

No production service, domain model, validator, serializer, clinical YAML, snapshot, golden, public API,
workflow, dependency, or lint configuration is changed.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded-task, targeted-verification, and close-procedure requirements.
- `docs/SAFETY_INVARIANTS.md` - purity, exact Decimal behavior, auditability, and safety constraints.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - Work Package 4 scope, required context properties,
  verification command, and acceptance gate.
- `src/cds/services/renal.py` - confirmed the calculator uses `localcontext()` and supplied no direct
  evidence of global-context mutation.
- `pyproject.toml` - confirmed the declared Python and focused pytest environment.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute a separate acceptance-verification task for the
merged Work Package 4 assertion correction in a complete repository checkout. Make no code changes unless
the focused failure proves a real defect, and run:

```bash
python -m pytest tests/unit/services/test_renal.py -q
```
