# CDS Platform Backlog

This file records unresolved decisions and explicitly deferred work. It does not identify the
active task or next action; see [`CURRENT.md`](CURRENT.md) for current execution state. Backlog
items are not approved implementation scope until they are resolved and documented in the
governing contract.

## Decisions needed before current vertical slice

These decisions must be resolved before the adult Cockcroft–Gault renal-dosing vertical slice can
be considered complete.

### Calculation and validation contract

Resolved calculator decisions are governed by
[`docs/RENAL_CALCULATOR_SPEC.md`](docs/RENAL_CALCULATOR_SPEC.md): Decimal precision and local
context, supported sex coefficients and fail-closed unsupported sex handling, calculator-side
unrounded storage and renal-band matching, no serum-creatinine floor or cap, renal-stability
meanings, exact first-slice units with no conversion, and minimum provenance for calculated renal
results.

- **Resolved — Age input:** birth date plus an explicit evaluation date is the only first-slice
  age-input API; completed-year, leap-day, invalid-date, and reproducibility behavior is governed
  by [`docs/RENAL_CALCULATOR_SPEC.md`](docs/RENAL_CALCULATOR_SPEC.md).
- **Deferred — Presentation formatting:** define any presentation-only scale or notation for a
  displayed renal value. Display formatting must remain outside the calculator and must not
  replace the underlying value used for rule matching.
- **Partially resolved — Result-state mapping:** missing renal stability maps to `incomplete`, and
  explicitly unstable renal function maps to `not_applicable`. Define remaining application-level
  assembly rules for `success`, `success_with_warnings`, other incomplete or not-applicable
  conditions, and unexpected `failed` results.
- **Partially resolved — Minimum provenance:** calculated renal-result provenance is defined.
  Define required provenance for manually entered inputs, matched rules, final recommendations,
  and the assembled top-level result.

### Renal content contract

The normative document shape, type rules, exact matching, renal-boundary semantics, content
versions, review states, reviewer fields, sources, and validation invariants are governed by
[`docs/RENAL_DOSE_CONTENT_SCHEMA.md`](docs/RENAL_DOSE_CONTENT_SCHEMA.md).

- **Partially resolved — Canonical identifiers:** exact first-slice medication IDs and identifier
  syntax are defined. [`docs/CEFEPIME_CONTENT_SELECTION.md`](docs/CEFEPIME_CONTENT_SELECTION.md)
  defines the initial cefepime identifiers.
  [`docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md`](docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md)
  defines the initial piperacillin–tazobactam source-context indication, route, formulation,
  standard-infusion, extended-infusion, regimen, content, rule, and source identifiers. Three
  source-based draft YAML documents now encode those exact piperacillin–tazobactam identifiers.
  Famotidine identifiers remain open for its scheduled source-selection task.
- **Partially resolved — Governing evidence:** the initial cefepime FDA-approved DailyMed source is
  recorded in [`docs/CEFEPIME_CONTENT_SELECTION.md`](docs/CEFEPIME_CONTENT_SELECTION.md).
  Piperacillin–tazobactam standard infusion uses the selected WG Critical Care DailyMed SPL, and its
  single extended-infusion variant uses the Patel et al. primary PK/PD publication recorded in
  [`docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md`](docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md).
  The three draft documents preserve the exact source IDs, versions, dates, citations, URLs, and
  evidence-level mappings selected there. The governing famotidine source remains open.
- **Partially resolved — Supported variants:** the initial cefepime set remains limited to four exact
  IV powder-for-solution maintenance regimens over 30 minutes. Three draft
  piperacillin–tazobactam documents now encode two exact FDA-labeled standard-infusion regimens and
  one exact primary-literature extended-infusion regimen. Pediatric, unstable-renal-function,
  renal-replacement-therapy, continuous-infusion, unlisted dose, unlisted frequency, and unlisted
  infusion variants remain unsupported. Famotidine variants remain open.
- **Partially resolved — Renal boundaries:** the selected cefepime source bands and maintenance
  matrix are recorded. The piperacillin–tazobactam standard-label matrices and extended-infusion
  less-than-or-equal-to `20 mL/min` adjustment threshold are now encoded as complete continuous
  draft partitions using unrounded values. Independent review must approve every interval
  representation before content is marked reviewed.
- **Open — Regulatory-label evidence level:** the version 1 schema lacks a `regulatory_label`
  evidence level. The cefepime and piperacillin–tazobactam selection records and draft documents
  provisionally map FDA-approved prescribing information to `guideline`. Independent review must
  approve that mapping or a separately scoped schema change is required before reviewed
  label-derived content is eligible for matching.
- **Partially resolved — Extended-infusion representation:** the piperacillin–tazobactam draft
  document provisionally represents the Patel publication with
  `hospitalized_serious_gram_negative_infection`, `formulation_id: null`, and a continuous
  less-than-or-equal-to `20 mL/min` adjustment band. Independent review must approve or replace those
  representations and confirm that the off-label modeling source is acceptable for the frozen
  prototype.
- **Partially resolved — Independent review:** required review fields and medication-specific
  attestations are defined for cefepime and piperacillin–tazobactam. All source-based documents
  remain `draft`; a named independent clinical-content reviewer is required before any may be marked
  `reviewed` or become eligible for rule matching.

## Later decisions

These decisions do not define the current task and must not be pulled into the first vertical
slice opportunistically.

- Whether a separately tested policy should calculate ideal or adjusted body weight from height
  and actual weight; the first slice expects the selected weight and `WeightType` to be supplied
  explicitly.
- Whether later input mappers should derive age from birth date and evaluation date beyond the
  minimal first-slice contract.
- Whether later workflows should support additional explicit unit conversions beyond the
  accepted first-slice units.
- How clinical-content version migration, retention, and version selection should work after the
  initial reviewed content set.
- Whether broader terminology services are needed after exact identifiers for the three supported
  medications and regimens are established.

## Deferred features

The following are explicitly outside the first vertical slice:

- additional medications or comprehensive renal dosing;
- estimated GFR equations, measured clearance workflows, or CKD staging;
- acute kidney injury detection or renal-trend analysis;
- intermittent hemodialysis, peritoneal dialysis, CRRT, or other renal replacement therapy;
- vancomycin or other therapeutic drug monitoring;
- anticoagulation, general risk scores, IV-to-PO conversion, allergies, interactions, hepatic
  dosing, pharmacogenomics, pregnancy, or pediatrics;
- API, FHIR, EHR, pharmacy-system, or production integration;
- interruptive alerts, autonomous actions, machine-learned recommendations, or generative
  clinical logic; and
- deployment, regulatory readiness, or clinical validation.