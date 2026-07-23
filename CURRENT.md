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

- Days 1–50 are complete.
- **Day 50 — Select and source piperacillin–tazobactam content** is complete.
- The next sequential task is **Day 51 — Encode and test piperacillin–tazobactam content**.

## Current state

- `docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md` now records one current FDA-approved DailyMed
  source for standard 30-minute infusion and one primary PK/PD publication for one
  extended-infusion variant.
- The selected standard source is the WG Critical Care piperacillin–tazobactam pharmacy-bulk-package
  SPL with DailyMed set ID `17a400ae-cbaa-4d07-95f4-c6917dfc0585`, SPL version `14`, record update
  date `2026-06-24`, version publication date `2026-07-03`, and labeling revision `11/2025`.
- The selected extended-infusion source is Patel et al., Antimicrobial Agents and Chemotherapy
  2010;54(1):460-465, DOI `10.1128/AAC.00296-09`, electronically published `2009-10-26`.
- The initial content set is limited to three exact supplied maintenance regimens:
  `3.375 g` IV every `6 hours` over `30 minutes`, `4.5 g` IV every `6 hours` over `30 minutes`, and
  `3.375 g` IV every `8 hours` over `240 minutes`.
- The standard-label non-dialysis matrices are recorded at greater than `40`, `20 to 40`, and less
  than `20 mL/min`. The extended-infusion candidate retains the parent regimen above `20 mL/min`
  and changes the interval to every `12 hours` at less than or equal to `20 mL/min`.
- Exact medication, route, formulation, source-context indication, regimen, content, rule, and
  source identifiers are documented. Total combined product dose remains explicit in `g`.
- The standard-label `guideline` evidence-level mapping, composite nosocomial-pneumonia source
  context, extended-infusion indication context, nullable formulation, off-label modeling source,
  and continuous unrounded interval representations remain provisional pending independent review.
- `BACKLOG.md` now marks piperacillin–tazobactam source, identifiers, selected variants, and source
  renal matrices as partially resolved while retaining the exact review blockers.
- No YAML content, rule, matcher, validation behavior, recommendation behavior, public import,
  serialized contract, medication scope, population, interface, or dependency changed.

## Verification

- Initial execution-context probe: `git rev-parse --show-toplevel` from `/mnt/data` failed because no
  repository checkout was present; no filesystem search or clone was attempted.
- A bounded documentation checkout was materialized at `/tmp/cds-platform` using only the task
  documents and generated replacements.
- Focused standard-library verification command completed successfully:
  `python /tmp/cds-platform/verify_day50.py`.
- The verification checked the prototype warning, both selected source identities and versions,
  three exact regimen records, standard and extended renal matrices, exact draft review metadata,
  explicit exclusions, backlog references, and the Day 51 next action.
- No pytest command was required because this task changes source-selection documentation and active
  state only; no executable behavior or test contract changed.
- No dependency was installed. No full-suite, lint, type-check, CI, or GitHub Actions passing claim
  is made.

## Files changed

- `docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md` — created.
- `BACKLOG.md` — updated.
- `CURRENT.md` — replaced with the current state and next action.

## Additional files inspected

- `AGENTS.md` — repository source hierarchy, bounded-checkout rules, clinical-content decisions, and
  close procedure.
- `docs/TASK_TEMPLATE.md` and `CDS_12_Week_Daily_Project_Plan.html` — task-template structure and the
  exact Day 50 deliverable.
- `docs/SAFETY_INVARIANTS.md`, `PROJECT_CHARTER.md`, and `FIRST_VERTICAL_SLICE.md` — required because
  Day 50 selects medication-specific clinical content inside the frozen scope.
- `BACKLOG.md` — existing unresolved piperacillin–tazobactam source, identifier, variant, boundary,
  and review decisions.
- `docs/RENAL_DOSE_CONTENT_SCHEMA.md` — exact identifier syntax, one-document-per-regimen contract,
  renal-boundary semantics, source fields, evidence levels, and review metadata.
- `docs/CEFEPIME_CONTENT_SELECTION.md` — directly relevant source-selection and review-record
  convention established by Day 43.
- The selected WG Critical Care DailyMed piperacillin–tazobactam SPL version 14 — exact product,
  label dates, adult indications, standard regimens, 30-minute administration, renal matrix, and
  warnings.
- Patel et al. 2010, DOI `10.1128/AAC.00296-09` — exact extended-infusion regimen, Cockcroft–Gault
  method, candidate renal adjustment threshold, PK/PD target, and modeling limitations.

## Active constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Structural and task-sufficiency validation must complete before calculation or rule matching.
- Missing, invalid, unsupported, ambiguous, unstable, and out-of-scope clinical facts fail closed
  without a dosing recommendation.
- Exact medication, regimen, source-context indication, route, formulation, total-product dose,
  frequency, infusion duration, renal unit, renal method, and content-version keys are matched
  without aliases, normalization, fuzzy matching, hidden component conversion, interpolation,
  extrapolation, fallback, or automatic version selection.
- Standard and extended infusion remain separate exact variants with separate governing sources.
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
- Exact source-based monitoring, warning, rationale, limitation, and immutable content-version text
  has not yet been authored.
- Until review is complete, all future source-based piperacillin–tazobactam documents must remain
  draft and cannot produce a successful recommendation through a rule.

## Next exact action

> Day 51 — encode and test the three exact piperacillin–tazobactam documents defined in
> `docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md`, preserving separate standard-label and
> extended-infusion sources, total combined-product dose units, complete non-dialysis renal
> partitions, exact source-context indications, explicit limitations, and `review.status: draft`;
> do not add another regimen or implement medication-specific engine behavior.
