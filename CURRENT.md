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

- Days 1–71 are complete.
- **Day 71 — Create the integration test matrix** is complete.
- The next sequential task is **Day 72 — Add full-flow parameterized tests**.

## Current state

- `docs/INTEGRATION_TEST_MATRIX.md` defines the Day 72 full-flow coverage before test implementation.
- The matrix inventories all six exact supported regimen variants: two cefepime, three
  piperacillin–tazobactam, and one famotidine regimen.
- Thirteen threshold rows expand to 39 immediately-below, exact-boundary, and immediately-above
  cases using unrounded Cockcroft–Gault `Decimal` values.
- Data-completeness cases distinguish initial validation failures from content-specific medication
  validation failures and state the expected stop point.
- Unsupported-context cases require exact identifiers and prohibit normalization, inference,
  conversion, interpolation, or adjacent-regimen fallback.
- Content and system-failure cases identify validation, repository, context, calculation, and rule
  failure injection points with fail-closed output requirements.
- Cross-case invariants require zero recommendations on every non-success outcome and preserve
  Decimal, UTC datetime, evidence, provenance, rule, content-version, and order-linkage contracts.
- Draft YAML remains ineligible; successful integration cases must use clearly labeled test-only
  reviewed in-memory copies without implying clinical review.
- No production code, clinical content, content review status, renal boundary, supported population,
  public interface, or serialized contract changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded documentation checkout was materialized at `/tmp/cds-platform` with only the new matrix
  and replacement active-state note.
- Structural matrix verification command:
  `python - <<'PY' ... PY` as recorded in the Day 71 task result.
- Structural verification result: all required regimen identifiers, 13 boundary families, 39
  expanded boundary cases, completeness, unsupported-context, failure, invariant, and Day 72 target
  sections were present.
- Pytest was not needed because Day 71 changes documentation only and does not alter executable
  behavior.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `docs/INTEGRATION_TEST_MATRIX.md` — added the exact-regimen, renal-boundary, data-completeness,
  unsupported-context, failure-injection, and cross-case coverage plan for Day 72.
- `CURRENT.md` — replaced with the Day 71 state and Day 72 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure and exact Day 71
  and Day 72 roadmap wording.
- `AGENTS.md` and `docs/SAFETY_INVARIANTS.md` — bounded execution, prototype, exact-input,
  fail-closed, auditability, and verification constraints.
- `src/cds/app/renal_dose.py` and `tests/unit/app/test_renal_dose.py` — orchestration order,
  validation stop points, exact repository lookup, and structured failure mappings.
- `tests/integration/test_cefepime_end_to_end.py` — existing test-only reviewed-content override and
  full-flow integration convention.
- `examples/cli_walkthrough_cases.json` — exact request-boundary identifiers and incomplete,
  unsupported, content-failure, and system-failure output conventions.
- The six current renal-content YAML files — exact regimen identifiers, formulations, renal bands,
  and threshold inclusivity for the supported cefepime, piperacillin–tazobactam, and famotidine
  variants.

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
- Draft content review eligibility remains separate from software integration-test eligibility.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 72 — implement `tests/integration/test_renal_dose_matrix.py` with parameterized full-flow cases
> for all six exact regimen variants, the 39 below/at/above renal-boundary cases, incomplete data,
> unsupported exact contexts, and structured content, calculation, and rule failures defined in
> `docs/INTEGRATION_TEST_MATRIX.md`.
