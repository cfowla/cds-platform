# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:

- repository cloning or broad filesystem searches for another checkout;
- GitHub Actions or CI investigation;
- workflow creation or modification;
- broad repository review; and
- substitute functional test runners.

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1-80 are complete.
- **Day 80 - Write the validation and missing-data policy** is implemented.
- The next sequential task is **Day 81 - Create the model and interface reference**.

## Current state

- `docs/DOMAIN_CONVENTIONS.md` now defines structural validation, task-sufficiency validation,
  combined tri-state validity, validation issue severity, and the requirement to validate before
  calculation, content matching, or rule evaluation.
- The policy documents exact first-slice units: body weight in `kg`, serum creatinine in `mg/dL`,
  and unindexed Cockcroft-Gault output in `mL/min`.
- Medication dose, frequency, and infusion quantities remain content-defined and must exactly match
  the selected reviewed content value and unit; no conversion, normalization, or alias matching was
  added.
- Missing numerics remain `None`; unknown categories remain explicit; missing and unsupported units
  remain separate blocking findings.
- The result-state policy maps exact supported recommendations to `success`, pre-computation
  validation failures to `incomplete`, post-validation exact nonmatches to `not_applicable`, and
  internal, content, or calculation failures to `failed`.
- `success_with_warnings` remains a defined enum value but is not currently emitted by the renal use
  case.
- `applied` and `passed` retain tri-state semantics, including the distinction between an
  unevaluated rule and an applied no-recommendation band.
- Unsupported causes are documented by detection stage rather than collapsed into one status. Every
  non-success outcome remains fail-closed and produces no dosing recommendation.
- `docs/SAFETY_INVARIANTS.md` now carries the concise working rules for the same validation layers,
  severity handling, units, state mapping, and unsupported-context behavior.
- No validation code, clinical content, calculation behavior, rule behavior, public import,
  serialized contract, dependency, interface, or logging configuration changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was created at `/tmp/cds-platform` containing the edited
  documentation and a task-specific documentation checker.
- Documentation structure command:
  `python /tmp/cds-platform/verify_validation_policy.py`
- Documentation structure result: passed; required policy sections, validation severities, all five
  result states, accepted units, fail-closed language, and 100-character line limits were present.
- Pytest was not required because the task changed documentation only and did not change executable
  behavior or a serialized software contract.
- No full-suite, lint, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `docs/DOMAIN_CONVENTIONS.md` - added the validation, missing-data, accepted-unit, severity,
  result-state, and unsupported-context policy.
- `docs/SAFETY_INVARIANTS.md` - added the concise corresponding safety rules.
- `CURRENT.md` - replaced with the Day 80 state and Day 81 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` - task structure and exact
  Day 80 and Day 81 roadmap wording.
- `AGENTS.md`, `PROJECT_CHARTER.md`, and `FIRST_VERTICAL_SLICE.md` - source hierarchy, validation
  requirements, scope, expected states, and fail-closed behavior.
- `src/cds/validation/models.py`, `patient.py`, `lab.py`, `renal.py`, and `medication.py` -
  implemented validation result shape, severity values, structural checks, sufficiency checks,
  exact units, and current error behavior.
- `src/cds/domain/enums.py` and `src/cds/domain/outputs.py` - result statuses and tri-state
  rule-result defaults.
- `src/cds/app/renal_dose.py` - validation combination, incomplete mapping, and structured failure
  mapping.
- `src/cds/services/renal.py` - validated-service boundary and exact renal input and output units.
- `src/cds/rules/engine.py` and `src/cds/rules/exact_renal_dose.py` - exact nonmatch, unsupported,
  no-recommendation, incomplete, and successful result mappings.

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

## Blockers

- A named independent content reviewer has not been identified.
- Draft content review eligibility remains separate from software contract-test eligibility.
- The current schema has no explicit supersession relationship or automatic active-version registry.
- Conflicting supplied versus declared body-weight type is not currently rejected before
  calculation.
- The famotidine adult minimum-weight boundary is not currently enforced in the full flow.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- The logging policy is not yet wired into application or interface failure paths.
- Focused Day 77 pytest execution remains unverified in this environment because no complete
  checkout or materialized application import graph was available.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 81 - document required versus optional fields, units, safe defaults, compatibility imports,
> canonical serialization, CLI request and response shapes, and current interface limitations
> without changing model, mapper, interface, or serialized contracts.
