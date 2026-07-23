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

- Days 1–53 are complete.
- **Day 53 — Select and source famotidine content** is complete.
- The next sequential task is **Day 54 — Encode and test famotidine content**.

## Current state

- `docs/FAMOTIDINE_CONTENT_SELECTION.md` records one exact, documentation-only famotidine source
  decision for the first renal-dose slice.
- The selected governing source is the FDA-approved DailyMed famotidine tablet label with set ID
  `4421ceb7-a114-436c-871a-7bc5444f8154`, SPL version `1`, record update date `2026-06-26`, and stated
  revision `06/2026`.
- The source record is explicitly identified as a repackaged label. Independent review must confirm
  its acceptability or replace it through a separately versioned source decision.
- Initial scope is limited to adults, stable renal function, unindexed Cockcroft–Gault in `mL/min`,
  no renal replacement therapy, oral film-coated tablets, exact indication
  `adult_symptomatic_nonerosive_gerd`, and the supplied parent regimen `20 mg` every `12 hours`.
- Candidate renal outcomes are `20 mg` every `12 hours` at creatinine clearance greater than or equal
  to `60 mL/min`, `20 mg` every `24 hours` from `30` to less than `60 mL/min`, and `20 mg` every
  `48 hours` below `30 mL/min`.
- Exactly `60 mL/min` is provisionally assigned to the no-adjustment band based on label section 8.6;
  independent review must approve that interpretation because the renal table uses the compact
  heading `30 to 60 mL/minute`.
- Alternate `10 mg` dosing, oral suspension, intravenous products, other indications, other parent
  regimens, pediatric use, unstable renal function, and renal replacement therapy remain unsupported.
- The future famotidine document must remain `draft` until source, boundary, maximum-dose,
  formulation, evidence-level, and safety-limit representations are independently reviewed.
- No YAML, rule, repository, service, domain model, public import, serialization contract, or clinical
  scope beyond the frozen famotidine medication was changed.

## Verification

- No repository checkout was available through this connector-only execution path; no filesystem
  search or clone was attempted.
- The Day 53 roadmap entry, task template, active state, safety invariants, first vertical-slice
  contract, analogous piperacillin–tazobactam selection record, backlog, and selected DailyMed label
  were inspected.
- Documentation was checked for the prototype warning, exact source identity and version, exact
  identifiers, explicit units, complete candidate renal partition, fail-closed exclusions, draft
  review metadata, reviewer attestations, and a bounded Day 54 handoff.
- `pytest` was not invoked because this task changes documentation only and no focused executable test
  applies. No dependency was installed.
- No full-suite, Ruff, type-check, CI, or GitHub Actions passing claim is made.

## Files changed

- `docs/FAMOTIDINE_CONTENT_SELECTION.md` — created.
- `BACKLOG.md` — updated with the selected famotidine source, identifiers, scope, boundaries, and open
  review decisions.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `docs/TASK_TEMPLATE.md` — bounded-task structure, verification, and close procedure.
- `CDS_12_Week_Daily_Project_Plan.html` — exact Day 53 deliverable and Day 54 boundary.
- `docs/SAFETY_INVARIANTS.md` — fail-closed matching, explicit units and context, versioned content,
  purity, and auditability constraints.
- `FIRST_VERTICAL_SLICE.md` — frozen three-medication scope, supported inputs, exclusions, and output
  contract.
- `docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md` — directly relevant source-selection and
  independent-review convention.
- The selected DailyMed famotidine tablet label — source identity, adult indication and parent dose,
  renal dosage table, alternate-formulation note, renal threshold statement, CNS warning, and QT
  limitation.

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
- The selected label describes maximum renal dosages; future content must not imply therapy selection
  or invent an alternate formulation.

## Blockers

- A named independent clinical-content reviewer has not been identified.
- The repackaged-label source choice, exactly-`60 mL/min` boundary interpretation, provisional
  `guideline` evidence mapping, and maximum-dose representation require independent review.

## Next exact action

> Day 54 — encode and test one draft famotidine renal-dose YAML document for the exact oral
> film-coated-tablet `20 mg` every `12 hours` symptomatic-nonerosive-GERD parent regimen, preserving
> the selected source, complete unrounded renal partition, explicit exclusions, and draft review
> status without implementing a rule.
