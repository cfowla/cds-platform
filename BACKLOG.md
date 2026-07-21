# CDS Platform Backlog

This file holds unresolved decisions and deferred work that must not expand the frozen initial renal-dosing scope. An item moves into implementation only after it is answered, documented in the governing scope, and paired with tests.

## Open questions for the renal vertical slice

### Domain and calculation contract

- Should the input contract accept an explicit integer age only, or also accept birth date plus evaluation date and calculate age at the mapping boundary?
- What exact `Sex` values will the configured Cockcroft–Gault implementation accept, and how will unsupported or unknown values be represented without silently choosing a coefficient?
- Will the first feature require the caller to supply the weight already selected for Cockcroft–Gault, or will a later separately tested policy calculate ideal or adjusted body weight from height and actual weight?
- Should calculator arithmetic use `Decimal` throughout, and what precision is required for the unrounded stored creatinine-clearance result?
- At what boundary should display rounding occur, and how will tests prove that rule matching uses the unrounded value?
- How will a test case explicitly attest that serum creatinine is sufficiently stable, and should absent stability information be `incomplete` or `not_applicable`?
- Are any serum-creatinine floors or caps permitted? The default answer is no unless a reviewed source and explicit scope amendment justify one.

### Result and validation behavior

- Which missing or unsupported conditions map to `incomplete` versus `not_applicable`, and which conditions represent the system state `failed`?
- What minimum provenance fields are required on manually entered inputs, calculated renal results, matched rules, and final recommendations?
- What canonical unit vocabulary and conversion policy will be accepted? Ambiguous units must remain rejected rather than inferred.
- What serialized representation is required for enums, timestamps, decimal values, assumptions, warnings, evidence, and provenance?

### Renal content

- What exact medication identifiers and regimen identifiers will be canonical for cefepime, piperacillin–tazobactam, and famotidine?
- Which authoritative sources and versions will govern each medication’s initial renal-adjustment content?
- Which indication, route, dose, frequency, and infusion-duration variants are supported for each medication?
- What are the exact renal boundaries and inclusivity rules, and how will content validation detect gaps, overlaps, or unreachable ranges?
- Who will perform the independent clinical-content review, and what reviewer metadata is required before a rule is treated as implemented?

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

## Next exact action

Implement `Sex`, `ResultStatus`, `RenalMethod`, and `WeightType` in `src/cds/domain/enums.py`, then replace `tests/unit/domain/test_enums.py` with value, string-serialization, and explicit unknown-state tests.
