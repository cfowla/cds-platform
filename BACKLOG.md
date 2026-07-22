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
  now defines the initial cefepime indication, route, formulation, regimen, content, rule, and
  source identifiers. Piperacillin–tazobactam and famotidine identifiers remain open for their
  scheduled source-selection tasks.
- **Partially resolved — Governing evidence:** the initial cefepime source is the selected
  FDA-approved DailyMed prescribing information recorded in
  [`docs/CEFEPIME_CONTENT_SELECTION.md`](docs/CEFEPIME_CONTENT_SELECTION.md). Governing sources for
  piperacillin–tazobactam and famotidine remain open.
- **Partially resolved — Supported variants:** the initial cefepime set is limited to four exact IV
  powder-for-solution maintenance regimens administered over 30 minutes and the explicitly listed
  indication identifiers. IM, pediatric, renal-replacement-therapy, extended-infusion, continuous-
  infusion, and other variants remain unsupported. Piperacillin–tazobactam and famotidine variants
  remain open.
- **Partially resolved — Renal boundaries:** the selected cefepime source bands and maintenance
  matrix are recorded. Independent review must approve the continuous unrounded interpretation of
  the source's integer-labeled `11 to 29` and `30 to 60` bands before content is marked reviewed.
- **Open — Regulatory-label evidence level:** the version 1 schema lacks a `regulatory_label`
  evidence level. The cefepime selection record proposes `guideline` as a documented provisional
  mapping. Independent review must approve that mapping or a separately scoped schema change is
  required before reviewed cefepime content is eligible for matching.
- **Partially resolved — Independent review:** required review fields and cefepime-specific
  attestations are defined. A named independent clinical-content reviewer remains required before
  any cefepime document may be marked `reviewed`.

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
