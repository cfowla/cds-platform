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
  `no-go`; this bounded lint-baseline correction does not certify a new release candidate.
- **INT-2 renal integration acceptance remains complete.**
- **Work Package 2 renal-content snapshot scope remains complete.**
- **Work Package 3 cefepime golden semantic review remains complete.**
- **Work Package 4 Decimal-context assertion correction and focused verification are complete.**
- **Work Package 5 Ruff-baseline selection and remediation are complete.**

## Work Package 5 result

Implemented from current `main` base commit `b6226f180b23149f216af65de917ddf06f0c025a`.

Root cause:

- `pyproject.toml` configured Ruff's target version and line length but left the selected lint rules
  implicit.
- Ruff 0.16.0 therefore enabled a broad default set and reproduced the release artifact's 284
  diagnostics.
- Of those diagnostics, 275 belonged to newly broad families outside the repository's previously
  implied `E4`, `E7`, `E9`, and `F` baseline. Those included 184 `FURB157` Decimal-constructor
  rewrites, 45 `UP017` timezone rewrites, and 12 `DTZ001` diagnostics, including deliberate
  timezone-naive negative-test inputs.
- The selected baseline contained nine `F401` unused-import diagnostics and one `E731` lambda
  assignment.

Approved bounded change:

- Added an explicit `[tool.ruff.lint]` selection of `E4`, `E7`, `E9`, and `F` in `pyproject.toml`.
- Removed two genuinely unused test imports.
- Added seven line-level `F401` suppressions with reasons for compatibility attributes that must remain
  available from `cds.domain.models` while remaining intentionally excluded from `__all__`.
- Replaced one assigned exception-throwing lambda in the integration failure test with an equivalent
  nested function.
- Did not use `--fix`, `--unsafe-fixes`, broad file-level ignores, or changes to Decimal construction,
  timezone-naive negative inputs, exception boundaries, clinical behavior, or public exports.

## Verification

Baseline capture used Ruff 0.16.0:

```bash
python -m ruff --version
python -m ruff check . --config pyproject.toml --show-settings
python -m ruff check . --config pyproject.toml
```

Baseline result:

- Version command exit status: 0; `ruff 0.16.0`.
- Settings command exit status: 0.
- Initial lint exit status: 1; 284 diagnostics, 261 reported fixable, and 7 additional hidden unsafe
  fixes.
- Complete effective settings and baseline diagnostics were captured in the isolated verification
  workspace. The raw files contain environment-specific absolute paths and are not published; the exact
  commands, Ruff version, exit statuses, and diagnostic counts are recorded here.

Final targeted verification:

```bash
python -m ruff check . --config pyproject.toml
python -m pytest tests/unit/domain/test_module_exports.py \
  tests/contract/test_renal_dose_interface_contracts.py \
  tests/unit/app/test_renal_dose.py \
  tests/integration/test_renal_dose_matrix.py::test_failures_are_structured_and_sanitized -q
```

Result:

- Final lint exit status: 0; `All checks passed!`.
- Focused pytest exit status: 0; 43 tests passed.

Supplemental full-suite verification:

```bash
python -m pytest -q
```

Result:

- Exit status: 1.
- 930 tests passed, 16 placeholder tests skipped, and 2 known strict xfails remained xfailed.
- `test_cefepime_golden_cases_byte_match_canonical_regeneration` failed at byte 1251 with the previously
  reviewed cefepime summary-casing mismatch.
- The full-suite failure is outside this lint-baseline task and was not hidden, reclassified, or
  repaired here.

## Remaining repair areas

1. Reconcile the cefepime golden byte mismatch still exposed by the supplemental full suite without
   weakening the test or overwriting the golden without semantic review.
2. **Work Package 6:** resolve placeholder skips and repair durable release-evidence capture.
3. **Work Package 7:** select and fully verify a new release candidate only after the preceding work
   packages are complete.
4. Tag the prototype milestone only after an explicit `go` decision for one exact unchanged candidate.

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

- The supplemental full suite still fails the cefepime canonical-regeneration byte comparison.
- Placeholder-skip dispositions, CLI evidence, clean candidate evidence, independent calculation
  approval, qualified content review, PHI review, release-custodian approval, and a final decision record
  remain incomplete.
- Existing known clinical and architecture limitations remain outside this task, including weight-type
  conflict handling, the famotidine adult minimum-weight boundary, content supersession, standalone CLI
  composition, and logging-policy wiring.

These blockers still prevent an honest release `go` or prototype milestone tag.

## Files changed

- `pyproject.toml` - makes the intended `E4`, `E7`, `E9`, and `F` Ruff ruleset explicit.
- `src/cds/domain/models.py` - narrowly documents intentional compatibility re-exports.
- `tests/contract/test_renal_dose_interface_contracts.py` - removes one unused import.
- `tests/unit/app/test_renal_dose.py` - removes one unused import.
- `tests/integration/test_renal_dose_matrix.py` - replaces one assigned throwing lambda with an
  equivalent nested function.
- `CURRENT.md` - records Work Package 5 completion, verification, limitations, and the next action.

No clinical content, snapshot, golden, dependency, workflow, validation, serialization, calculator, or
public-contract behavior was changed.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` - bounded-task, targeted-verification, and close-procedure requirements.
- `docs/SAFETY_INVARIANTS.md` - purity, exact Decimal behavior, auditability, and safety constraints.
- `docs/PROTOTYPE_RELEASE_REMEDIATION_PLAN.md` - Work Package 5 scope, classification constraints,
  verification command, and acceptance gate.
- `BACKLOG.md` - confirmed that rule selection and intentional negative-test diagnostics required a
  policy decision.
- `tests/unit/domain/test_module_exports.py` - confirmed compatibility attributes must remain module
  attributes while staying outside `__all__`.

## Next exact action

Use `docs/TASK_TEMPLATE.md` to formulate and execute a separate bounded task that first reconciles the
cefepime golden byte mismatch still exposed by the full suite, preserving the prior semantic-review
requirements and changing only the affected golden or generator after the exact difference is confirmed.
