# Current Work

This file is replaced after every task. It is not an append-only diary.

## Repository execution mode

Use the repository checkout supplied by the execution environment. If no checkout is available,
use the GitHub connector to materialize only the named files and concretely required imports in a
bounded verification checkout.

GitHub is the authoritative source and destination for repository files.

Prohibited unless explicitly requested:
- repository cloning or filesystem searches for another checkout
- GitHub Actions or CI investigation
- workflow creation or modification
- broad repository review
- substitute functional test runners

External source retrieval is permitted only when a bounded clinical-content source-selection task
explicitly requires it. Use the named authoritative source and do not broaden into general web
research.

Use only the named files and task-specified commands. Do not install missing test dependencies.

## Roadmap position

- Days 1–51 are complete.
- **Day 51 — Encode and test piperacillin–tazobactam content** is complete.
- The next sequential task is **Day 52 — Add piperacillin–tazobactam rule coverage**.

## Current state

- Three exact source-based piperacillin–tazobactam renal-dose documents now exist under
  `src/cds/content/renal/` with immutable content version `1.0.0-draft`.
- The standard-infusion documents encode `3.375 g` IV every `6 hours` over `30 minutes` and `4.5 g`
  IV every `6 hours` over `30 minutes`, using the selected WG Critical Care DailyMed SPL version 14.
- The extended-infusion document encodes `3.375 g` IV every `8 hours` over `240 minutes`, using Patel
  et al. as the governing dosing source and the selected DailyMed label only for explicitly separated
  safety-monitoring statements.
- Standard-label content preserves the complete non-dialysis partitions greater than `0` and less
  than `20`, `20` through `40`, and greater than `40 mL/min` with exact endpoint ownership.
- Extended-infusion content preserves the complete draft partition greater than `0` through `20` and
  greater than `20 mL/min`, changing only the interval from every `8` to every `12 hours` in the lower
  band.
- All base and recommendation doses remain total combined piperacillin–tazobactam product in `g`;
  frequency uses `hours`, infusion duration uses `minutes`, and no hidden component conversion occurs.
- Every document retains exact medication, regimen, indication, route, formulation, rule, source, and
  content identifiers; explicit rationale, monitoring, provenance, and limitations; and the prototype
  clinical-use prohibition.
- Every document remains `review.status: draft` with null reviewer fields and is ineligible for rule
  matching until independent clinical-content review is completed.
- Focused tests lock the repository to the three selected documents, verify both renal matrices and
  boundaries, check source provenance and draft state, and prove four unselected infusion variants are
  not encoded.
- No piperacillin–tazobactam rule, matcher, repository eligibility behavior, application workflow,
  public import, serialized contract, dependency, interface, medication scope, or population changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with only the three new
  content documents and the focused Day 51 test.
- Available tools were Python `3.13.5`, pytest `9.0.2`, and PyYAML `6.0.3`; no dependency was installed.
- Focused collection completed successfully:
  `python -m pytest tests/unit/repositories/test_piperacillin_tazobactam_content.py --collect-only -q`.
- Result: `17 tests collected in 0.03s`.
- Focused execution completed successfully:
  `python -m pytest tests/unit/repositories/test_piperacillin_tazobactam_content.py -q`.
- Result: `17 passed in 0.22s`.
- `python -m compileall -q tests/unit/repositories/test_piperacillin_tazobactam_content.py`
  completed successfully.
- The full suite was not run because no complete checkout was available and Day 51 does not change a
  shared implementation contract.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/content/renal/piperacillin_tazobactam_standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes.yaml` — created.
- `src/cds/content/renal/piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes.yaml` — created.
- `src/cds/content/renal/piperacillin_tazobactam_extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes.yaml` — created.
- `tests/unit/repositories/test_piperacillin_tazobactam_content.py` — created.
- `BACKLOG.md` — updated.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `AGENTS.md` — source hierarchy, bounded-checkout rules, clinical-content boundaries, verification,
  and close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task-template
  structure and the exact Day 51 deliverable.
- `docs/SAFETY_INVARIANTS.md`, `PROJECT_CHARTER.md`, and `FIRST_VERTICAL_SLICE.md` — required because
  Day 51 authors medication-specific clinical content inside the frozen renal-dose scope.
- `CURRENT.md` and `BACKLOG.md` — active task, exact next action, and unresolved review and
  representation decisions.
- `docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md` — authoritative selected sources, identifiers,
  regimens, renal matrices, monitoring sections, limitations, and review requirements.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — version 1 document shape, exact identifier syntax, quoted
  clinical decimals, interval semantics, evidence fields, and review-state contract.
- `src/cds/repositories/renal_content_schema.py` — existing generic closed-schema boundary; no
  medication-specific logic was added.
- The Day 44 cefepime source-based YAML and focused content-test convention — directly relevant
  repository pattern for source-linked draft documents and bounded content tests.
- The selected WG Critical Care DailyMed SPL version 14 and Patel et al. 2010 publication — used only
  to confirm already selected dose matrices, infusion strategies, source metadata, monitoring text,
  and recorded limitations.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, source-context indication, route, formulation, total-product dose,
  frequency, infusion duration, renal unit, renal method, and content-version keys are matched
  without aliases, normalization, fuzzy matching, hidden component conversion, interpolation,
  extrapolation, fallback, or automatic version selection.
- Standard and extended infusion remain separate exact variants with separate governing dosing
  sources.
- The prototype does not select therapy, infer an indication or organism, interpret MICs, verify a
  companion aminoglycoside, select duration, or extrapolate to unlisted infusion strategies.
- Clinical decimal values and units remain explicit; renal-band matching uses the stored unrounded
  value.
- Draft or retired content is never eligible for rule matching. Software verification does not
  confer clinical review status.
- Do not invent reviewer identity, resolve source ambiguity silently, or treat source ranges or
  modeling results as authorization for the prototype to select an initial regimen.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The reviewer must approve or replace the standard-label continuous boundary representation, the
  positive renal-domain lower bound, the composite nosocomial-pneumonia source-context identifier,
  and the provisional `guideline` evidence-level mapping.
- The reviewer must approve or replace the extended-infusion source-context indication,
  `formulation_id: null`, less-than-or-equal-to `20 mL/min` continuous partition, and use of the
  off-label PK/PD modeling publication for the frozen prototype.
- The reviewer must verify the exact source transcription, monitoring text, total-product dose
  interpretation, and separation of the extended-infusion dosing source from label-derived safety
  monitoring.
- Until review is complete, all three documents remain draft and cannot produce a successful
  recommendation through a rule.

## Next exact action

> Day 52 — add piperacillin–tazobactam rule coverage by reusing the existing generic exact-regimen
> matcher where possible, requiring exact medication, source-context indication, route, formulation,
> total-product dose, frequency, infusion duration, renal method, renal unit, and reviewed content
> context; preserve explicit unsupported outcomes and do not add medication-specific engine behavior.