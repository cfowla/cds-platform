# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:
- repository cloning or broad filesystem searches for another checkout
- GitHub Actions or CI investigation
- workflow creation or modification
- broad repository review
- substitute functional test runners

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–75 are complete.
- **Day 75 — Add property and invariant tests** is implemented.
- The next sequential task is **Day 76 — Add logging policy**.

## Current state

- `tests/integration/test_renal_safety_invariants.py` adds deterministic property-style and
  fail-closed invariant coverage without adding Hypothesis or another dependency.
- All eight current renal-dose YAML documents are probed at each declared endpoint, immediately
  below and above each endpoint, interval midpoints, and the unbounded upper tail.
- Every in-domain probe must match exactly one renal band, and no probe may match more than one
  band.
- Three representative critical validation failures—missing birth date, body-weight value, and
  serum-creatinine value—must remain invalid, stop before a renal result, and produce no
  recommendation.
- The six established full-flow regimen variants are exercised once per renal band through
  `RenalDoseUseCase` using clearly labeled test-only reviewed copies of draft content.
- Every successful rule result, clinician-facing recommendation, and dose recommendation must retain
  nonempty evidence and exact rule-content provenance.
- Every recommendation evidence item must retain a nonunknown evidence level, citation, source
  document, source version, source identifier, and content version.
- No production code, clinical content, content review status, renal boundary, supported medication,
  public interface, serialized contract, or dependency changed.
- The Day 72 strict expected-failure cases remain unchanged.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification path was used at `/tmp/cds-platform` for the new test module only.
- Pytest 9.0.2 was available in the supplied environment.
- Syntax verification command:
  `python -m py_compile tests/integration/test_renal_safety_invariants.py`
- Syntax verification result: passed.
- A structural line-length check found no lines longer than the configured 100-character limit.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/integration/test_renal_safety_invariants.py`
  `--collect-only -q`
- Focused collection stopped because the bounded checkout did not contain the repository source
  package: `ModuleNotFoundError: No module named 'cds'`.
- No focused execution, full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `tests/integration/test_renal_safety_invariants.py` — added eight-document renal-band partition
  probes, critical-validation fail-closed checks, and six-regimen successful traceability
  invariants.
- `CURRENT.md` — replaced with the Day 75 state and Day 76 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact
  Day 75
  and Day 76 roadmap wording.
- `AGENTS.md`, `docs/SAFETY_INVARIANTS.md`, and the prior `CURRENT.md` — bounded execution,
  prototype, validation-order, fail-closed, auditability, and close-procedure requirements.
- `tests/integration/test_renal_dose_matrix.py` — established six-regimen full-flow fixtures,
  validation stop behavior, reviewed test-copy convention, and existing boundary assertions.
- `tests/contract/test_renal_content_snapshots.py` — exact set of eight current renal-content
  documents and their current renal-band partitions.
- `src/cds/repositories/renal_content.py`, `src/cds/rules/predicates.py`, and
  `src/cds/rules/exact_renal_dose.py` — typed content, exact endpoint semantics, one-band
  enforcement,
  and successful evidence and provenance construction.
- `src/cds/domain/outputs.py`, `src/cds/domain/support.py`, and
  `src/cds/validation/models.py` — traceability fields and critical validation severity contract.
- `src/cds/validation/patient.py` — adult and body-weight structural error behavior used by the
  critical-validation invariant.
- `tests/unit/repositories/test_renal_content_schema.py` — existing schema-level overlap, gap, and
  shared-boundary rejection coverage.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Draft clinical content is not eligible for production rule matching and has not received
  independent clinical-content review.
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

## Blockers

- A named independent content reviewer has not been identified.
- Draft content review eligibility remains separate from software contract-test eligibility.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 76 — add a logging policy that excludes patient identifiers and sensitive payloads by default,
> and test that failures and diagnostics do not unnecessarily disclose synthetic case details,
> without changing clinical scope, interface contracts, or production recommendation behavior.
