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

- Days 1–54 are complete.
- **Day 54 — Encode and test famotidine content** is complete.
- The next sequential task is **Day 55 — Add famotidine rule coverage**.

## Current state

- One exact source-based famotidine renal-dose document now exists at
  `src/cds/content/renal/famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml` with immutable
  content version `1.0.0-draft`.
- The document encodes only oral film-coated tablets, exact indication
  `adult_symptomatic_nonerosive_gerd`, and the supplied parent regimen `20 mg` every `12 hours`.
- The complete positive unrounded Cockcroft–Gault partition is greater than `0` to less than `30`,
  `30` to less than `60`, and greater than or equal to `60 mL/min`.
- The corresponding source-based outcomes are `20 mg` every `48`, `24`, and `12 hours`; exactly
  `60 mL/min` is provisionally assigned to the no-adjustment band based on label section 8.6.
- Dose values remain explicit in `mg`, frequency intervals in `hours`, and infusion duration is
  explicitly `null` for the oral regimen.
- The selected Sportpharm DailyMed set ID, SPL version, update date, stated label revision, repackaged
  label status, citation, source URL, rationale, monitoring, limitations, and provenance are retained.
- The document remains `review.status: draft` with null reviewer fields and is ineligible for rule
  matching until independent clinical-content review is completed.
- Focused tests lock the repository to the single selected document, verify exact identifiers and
  units, renal matrices and endpoint ownership, source provenance, draft state, explicit exclusions,
  and unsupported oral suspension, intravenous, 10 mg, and alternate tablet regimens.
- No famotidine rule, matcher, repository eligibility behavior, schema, public import, serialization
  contract, dependency, interface, medication scope, or population changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- A bounded verification checkout was materialized at `/tmp/cds-platform` with only the new content
  document and focused Day 54 test.
- Focused execution completed successfully:
  `python -m pytest tests/unit/repositories/test_famotidine_content.py -q`.
- Result: `10 passed in 0.21s`.
- No dependency was installed.
- The full suite was not run because no complete checkout was available and Day 54 does not change a
  shared implementation contract.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `src/cds/content/renal/famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml` — created.
- `tests/unit/repositories/test_famotidine_content.py` — created.
- `BACKLOG.md` — updated.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — bounded-task structure and the
  exact Day 54 deliverable.
- `docs/SAFETY_INVARIANTS.md` — fail-closed matching, explicit units and context, versioned content,
  purity, and auditability constraints.
- `CURRENT.md` and `BACKLOG.md` — active task, exact next action, and unresolved famotidine review and
  representation decisions.
- `docs/FAMOTIDINE_CONTENT_SELECTION.md` — authoritative selected source, identifiers, exact regimen,
  renal matrix, exclusions, limitations, and review requirements.
- `docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md`, one Day 51 source-based YAML document, and its
  focused content tests — directly relevant source-linked draft-content and test conventions.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Validate structure and task sufficiency before calculation or matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope facts fail closed without a
  dosing recommendation.
- Match exact medication, indication, route, formulation, dose, frequency, renal method, renal unit,
  indexing state, stability, renal replacement therapy, and content version without aliases,
  normalization, conversion, inference, interpolation, extrapolation, fallback, or automatic version
  selection.
- Preserve unrounded Decimal renal values and explicit interval ownership.
- Draft or retired content is never eligible for rule matching. Software verification does not confer
  clinical review status.
- The selected label describes maximum renal dosages; the prototype must not imply therapy selection
  or invent an alternate formulation.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The repackaged-label source choice, exactly-`60 mL/min` boundary interpretation, provisional
  `guideline` evidence mapping, maximum-dose representation, formulation representation, source
  transcription, monitoring text, and exclusions require independent review.

## Next exact action

> Day 55 — add famotidine rule coverage by reusing the existing generic exact-regimen matcher where
> possible, requiring exact medication, source-context indication, oral route, film-coated-tablet
> formulation, `20 mg` dose, `12 hours` frequency, null infusion duration, renal method, renal unit,
> stable non-RRT context, and reviewed content; preserve explicit unsupported outcomes and do not add
> medication-specific engine behavior.
