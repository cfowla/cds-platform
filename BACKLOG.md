# CDS Platform Backlog

This file records unresolved decisions and explicitly deferred work. It does not identify the active task or next action; see [`CURRENT.md`](CURRENT.md) for current execution state. Backlog items are not approved implementation scope until they are resolved and documented in the governing contract.

## Decisions needed before current vertical slice

These decisions must be resolved before the adult Cockcroft–Gault renal-dosing vertical slice can be considered complete.

### Calculation and validation contract

- **Partially resolved — Age input:** the stable feature contract permits an evaluation date or a supplied calculated age. Decide the exact input fields, mapper responsibility, and reproducibility metadata for age used by the calculation.
- **Partially resolved — Sex handling:** the domain vocabulary includes `male`, `female`, `other`, and `unknown`. Decide which values the configured Cockcroft–Gault implementation accepts and how unsupported values fail closed without selecting a coefficient.
- **Open — Arithmetic precision:** decide the `Decimal` calculation context and required precision for the stored, unrounded creatinine-clearance result.
- **Partially resolved — Rounding boundary:** calculations and rule matching must use the unrounded value. Define the display-rounding rule and tests proving that renal-band matching does not use the rounded value.
- **Open — Renal stability:** define how a synthetic test case attests that serum creatinine is sufficiently stable and whether absent stability information produces `incomplete` or `not_applicable`.
- **Partially resolved — Serum-creatinine floors or caps:** the default is no floor or cap. Codify and test that behavior; any exception requires a reviewed source and explicit scope amendment.
- **Partially resolved — Result-state mapping:** `ResultStatus` defines `success`, `success_with_warnings`, `incomplete`, `not_applicable`, and `failed`. Define the exact clinical and system conditions that map to each non-success state.
- **Open — Minimum provenance:** define the required provenance fields for manually entered inputs, calculated renal results, matched rules, and final recommendations.
- **Partially resolved — Units and conversion:** ambiguous units are rejected and units are never inferred silently. Define the accepted unit vocabulary and any explicitly supported conversion paths for the first slice.

### Renal content contract

- **Open — Canonical identifiers:** define the exact medication and regimen identifiers for cefepime, piperacillin–tazobactam, and famotidine.
- **Open — Governing evidence:** select the authoritative sources and versions for each medication's initial renal-adjustment content.
- **Open — Supported variants:** define the supported indication, route, dose, frequency, infusion-duration, formulation, and regimen variants for each medication.
- **Open — Renal boundaries:** define exact renal bands and inclusivity rules, plus content validation for gaps, overlaps, contradictions, and unreachable ranges.
- **Open — Independent review:** identify the clinical-content reviewer and required reviewer metadata before a rule is treated as implemented.

## Later decisions

These decisions do not define the current task and must not be pulled into the first vertical slice opportunistically.

- Whether a separately tested policy should calculate ideal or adjusted body weight from height and actual weight; the first slice expects the selected weight and `WeightType` to be supplied explicitly.
- Whether later input mappers should derive age from birth date and evaluation date beyond the minimal first-slice contract.
- Whether later workflows should support additional explicit unit conversions beyond the accepted first-slice units.
- How clinical-content version migration, retention, and version selection should work after the initial reviewed content set.
- Whether broader terminology services are needed after exact identifiers for the three supported medications and regimens are established.

## Deferred features

The following are explicitly outside the first vertical slice:

- additional medications or comprehensive renal dosing;
- estimated GFR equations, measured clearance workflows, or CKD staging;
- acute kidney injury detection or renal-trend analysis;
- intermittent hemodialysis, peritoneal dialysis, CRRT, or other renal replacement therapy;
- vancomycin or other therapeutic drug monitoring;
- anticoagulation, general risk scores, IV-to-PO conversion, allergies, interactions, hepatic dosing, pharmacogenomics, pregnancy, or pediatrics;
- API, FHIR, EHR, pharmacy-system, or production integration;
- interruptive alerts, autonomous actions, machine-learned recommendations, or generative clinical logic; and
- deployment, regulatory readiness, or clinical validation.
