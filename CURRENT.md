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

- Days 1–74 are complete.
- **Day 74 — Add content snapshot tests** is implemented.
- The next sequential task is **Day 75 — Add property and invariant tests**.

## Current state

- `tests/contract/test_renal_content_snapshots.py` adds one review-oriented snapshot contract across
  all eight current renal-dose YAML documents.
- The baseline protects the exact content-document set and makes schema, content, rule, medication,
  regimen, indication, route, formulation, dose, interval, and infusion changes visible together.
- Supported age, renal method, renal unit, renal stability, and renal-replacement-therapy facts are
  protected without reproducing clinical-content logic in production modules.
- Every renal band protects its identifier, lower and upper bounds with inclusivity, outcome,
  recommendation action, dose, route, frequency, infusion duration, and governing source IDs.
- Source identifiers, evidence levels, source versions, and publication dates are protected for the
  cefepime, piperacillin–tazobactam, extended-infusion, and famotidine content sources.
- Review status, reviewed content version, reviewer, reviewer role, and review date are protected.
- A separate assertion requires every current content version and review record to remain draft and
  unreviewed; software snapshot coverage does not imply independent clinical approval.
- No snapshot plugin or new dependency was added. The test uses the existing pytest and PyYAML
  dependencies and ordinary Python structures so changes produce inspectable pytest diffs.
- No production code, clinical content, content review status, renal boundary, supported medication,
  eligibility rule, interface behavior, or serialized contract changed.
- The Day 72 strict expected-failure cases remain unchanged.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification path was used at `/tmp/cds-platform` for the new contract module only.
- Pytest 9.0.2 and PyYAML 6.0.3 were available in the supplied environment.
- Syntax verification command:
  `python -m py_compile tests/contract/test_renal_content_snapshots.py`
- Syntax verification result: passed.
- A structural line-length check found no lines longer than the configured 100-character limit.
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/contract/test_renal_content_snapshots.py --collect-only -q`
- Focused collection result: passed; 2 tests collected.
- Focused execution was not run because the bounded checkout did not contain the eight production
  renal-content YAML resources. No full-suite, lint, type-check, CI, or GitHub Actions passing claim
  is made.

## Files changed

- `tests/contract/test_renal_content_snapshots.py` — added the eight-document source, version,
  review, supported-context, renal-band, and recommendation snapshot contract.
- `CURRENT.md` — replaced with the Day 74 state and Day 75 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact
  Day 74 and Day 75 roadmap wording.
- `AGENTS.md`, `docs/SAFETY_INVARIANTS.md`, and the prior `CURRENT.md` — bounded execution,
  prototype, auditability, clinical-content separation, and close-procedure requirements.
- `tests/unit/repositories/test_cefepime_content.py`,
  `tests/unit/repositories/test_piperacillin_tazobactam_content.py`, and
  `tests/unit/repositories/test_famotidine_content.py` — current document names, exact regimen
  matrices, renal boundaries, source versions, and draft review conventions.
- Representative piperacillin–tazobactam source and review sections were inspected directly to
  confirm the standard-label and extended-infusion provenance strings used by the snapshot.
- Recent Day 73 repository commits were inspected to confirm the authoritative base and current
  roadmap state.

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

> Day 75 — add property and invariant tests enforcing exactly one matched renal band, no overlap,
> no recommendation after critical validation failure, and required evidence and provenance on every
> successful recommendation, without changing clinical scope or production behavior.
