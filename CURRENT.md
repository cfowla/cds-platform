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

- Days 1–70 are complete.
- **Day 70 — Weekly review: manual CLI walkthrough** is complete.
- The next sequential task is **Day 71 — Create the integration test matrix**.

## Current state

- `examples/cli_walkthrough.py` provides one reproducible synthetic harness around the existing
  dependency-injected renal-dose CLI boundary.
- `examples/cli_walkthrough_cases.json` saves exact request overrides, canned structured use-case
  results, canonical-output snapshots, expected exit codes, and sanitized stderr fragments for
  cefepime, piperacillin–tazobactam, famotidine, incomplete, unsupported, content-failure, and
  system-failure scenarios.
- The three medication walkthroughs exercise the interface contract with clearly labeled synthetic
  recommendations and evidence; the saved results do not validate clinical content or dosing logic.
- Incomplete, unsupported, content-failure, and system-failure scenarios remain fail-closed and
  contain no recommendation.
- Verification compares deterministic canonical JSON byte-for-byte, confirms the expected exit
  code and stderr fragment, and requires exactly one configured use-case invocation per scenario.
- `--summary` remains presentation-only on stderr, and `--output` writes canonical JSON exclusively
  to the requested path.
- `docs/CLI_WALKTHROUGH.md` records macOS, Linux, and Windows commands, expected outcomes, the
  dependency-injected composition limitation, and the non-clinical status of canned results.
- `README.md` now points to the saved walkthrough instead of describing the CLI as an empty scaffold
  or presenting the dependency-injected module as a standalone executable.
- No production clinical logic, clinical content, calculator, validation, rule, repository,
  application, mapper, domain model, canonical serializer, or CLI behavior changed.

## Verification

- The required `git rev-parse --show-toplevel` probe was run once from `/` and did not identify a
  repository checkout.
- No repository clone, dependency installation, substitute runner, CI, or GitHub Actions
  investigation was attempted.
- GitHub was authoritative for source retrieval and final repository changes.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with the new walkthrough
  files and only the existing CLI, request/response mapper, DTO, passive domain, and canonical
  serializer imports concretely required for execution.
- Git blob hashes for the new walkthrough files and all connector-fetched source dependencies matched
  their GitHub blob SHAs before execution.
- The environment supplied pytest 9.0.2.
- Walkthrough verification command:
  `PYTHONPATH=src python examples/cli_walkthrough.py --verify`
- Walkthrough result: `7 synthetic CLI walkthrough scenarios verified.`
- Focused collection command:
  `PYTHONPATH=src python -m pytest tests/unit/interfaces/test_cli_walkthrough.py --collect-only -q`
- Collection result: `2 tests collected in 0.00s`.
- Focused test command:
  `PYTHONPATH=src python -m pytest tests/unit/interfaces/test_cli_walkthrough.py -q`
- Test result: `2 passed in 0.57s`.
- Compile command:
  `python -m compileall -q examples/cli_walkthrough.py tests/unit/interfaces/test_cli_walkthrough.py src/cds/interfaces/cli.py src/cds/mappers/renal_dose_request.py src/cds/mappers/renal_dose_response.py src/cds/utils/serialization.py`
- Compile result: completed with no output or error.
- Manual success, incomplete, summary, and output-path checks confirmed exit codes `0` and `2`,
  canonical statuses `success` and `incomplete`, prototype warning text, no recommendation in the
  incomplete summary, no stdout when `--output` was used, and successful canonical file output.
- The changed Python files contain no lines over the configured 100-character limit.
- Ruff was not installed in the supplied environment, so no lint passing claim is made.
- No full-suite, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `examples/cli_walkthrough.py` — added the reproducible dependency-injected scenario runner and
  deterministic snapshot verifier.
- `examples/cli_walkthrough_cases.json` — added seven synthetic request/result/exit snapshots.
- `docs/CLI_WALKTHROUGH.md` — documented commands, outcomes, limitations, and prototype warnings.
- `tests/unit/interfaces/test_cli_walkthrough.py` — added focused execution, scenario-coverage, and
  fail-closed checks.
- `README.md` — replaced stale scaffold commands with the saved walkthrough command and limitations.
- `CURRENT.md` — replaced with the Day 70 state and Day 71 next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task structure, Day 70 scope,
  and Day 71 roadmap wording.
- `AGENTS.md` and `docs/SAFETY_INVARIANTS.md` — bounded execution, prototype, fail-closed,
  no-inference, sensitive-data, architecture, and verification constraints.
- `src/cds/interfaces/cli.py` and `tests/unit/interfaces/test_cli.py` — dependency injection,
  canonical output, summary, sanitized diagnostics, and explicit exit-code contracts.
- `src/cds/mappers/renal_dose_request.py`, `src/cds/mappers/renal_dose_response.py`,
  `src/cds/app/dto.py`, and `src/cds/utils/serialization.py` — exact request and canonical response
  boundaries used by the walkthrough.
- `src/cds/domain/clinical.py`, `src/cds/domain/enums.py`, `src/cds/domain/support.py`, and
  `src/cds/domain/value_objects.py` — direct passive dependencies required for bounded execution.
- `src/cds/app/renal_dose.py`, `tests/unit/app/test_renal_dose.py`,
  `src/cds/repositories/renal_content.py`, `src/cds/rules/engine.py`, and
  `src/cds/rules/registry.py` — configured-use-case and exact rule/content boundary conventions.
- Existing piperacillin–tazobactam and famotidine content/rule commits — exact synthetic request
  identifiers and regimen shapes used in the saved walkthrough inputs.
- `pyproject.toml` and `README.md` — configured verification and user-facing command conventions.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Canned walkthrough results verify interface behavior only and must not be represented as clinical
  calculation, content, dosing, or independent-review validation.
- Validate structure and task sufficiency before calculation or rule matching.
- Unsupported or insufficient cases remain fail-closed and produce no recommendation.
- Keep identifiers and units exact and case-sensitive; do not normalize, infer, alias, or fall back.
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
- Draft content review eligibility remains separate from this synthetic interface walkthrough.
- The production CLI remains a dependency-injected boundary without a standalone composition root.
- Full-repository verification was not available in the supplied execution context.

## Next exact action

> Day 71 — create the integration test matrix by listing data-completeness states, all three
> medications, regimen variants, renal boundaries, unsupported contexts, and system-failure
> combinations before implementing the full-flow parameterized tests.
