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

- **Resolved for the selected set — Canonical identifiers:** exact first-slice medication IDs and
  identifier syntax are defined. [`docs/CEFEPIME_CONTENT_SELECTION.md`](docs/CEFEPIME_CONTENT_SELECTION.md)
  defines the selected cefepime identifiers.
  [`docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md`](docs/PIPERACILLIN_TAZOBACTAM_CONTENT_SELECTION.md)
  defines the selected piperacillin–tazobactam identifiers.
  [`docs/FAMOTIDINE_CONTENT_SELECTION.md`](docs/FAMOTIDINE_CONTENT_SELECTION.md) defines the selected
  famotidine content, rule, source, indication, route, formulation, dose, and frequency identifiers.
- **Resolved for the selected set — Governing evidence:** the selected cefepime and standard-infusion
  piperacillin–tazobactam DailyMed sources, the Patel et al. extended-infusion source, and the selected
  Sportpharm famotidine DailyMed SPL version 1 were included in the completed qualified independent
  clinical-content review. The versioned documents retain exact source identifiers, versions, dates,
  citations, and limitations.
- **Resolved for the selected set — Supported variants:** reviewed content remains limited to four
  exact cefepime IV powder-for-solution maintenance regimens over 30 minutes, two exact labeled
  piperacillin–tazobactam standard-infusion regimens, one exact primary-literature extended-infusion
  regimen, and one exact famotidine oral film-coated-tablet regimen for
  `adult_symptomatic_nonerosive_gerd`. All unlisted variants remain unsupported.
- **Resolved for the selected set — Renal boundaries:** the exact continuous Decimal partitions and
  boundary ownership recorded in the eight selected documents were included in the independent
  clinical-content review, including cefepime boundaries, piperacillin–tazobactam 20 and 40 mL/min
  boundaries, and famotidine assignment of exactly 60 mL/min to the no-adjustment band.
- **Resolved for the selected versions — Regulatory-label evidence level:** the qualified review
  accepted the version 1 schema's `guideline` evidence-level mapping for the selected FDA-approved
  prescribing-information sources. A future schema may add `regulatory_label`, but that is not a
  blocker for these exact reviewed versions.
- **Resolved for the selected version — Extended-infusion representation:** the qualified review
  included the Patel publication, `hospitalized_serious_gram_negative_infection`,
  `formulation_id: null`, the continuous positive renal domain, and the less-than-or-equal-to
  `20 mL/min` adjustment threshold. The document continues to disclose its off-label modeling basis,
  target limitations, and unsupported extrapolations.
- **Resolved for the selected version — Famotidine maximum-dose representation:** the qualified review
  included the repackaged FDA-approved source, recommended-maximum-dose interpretation, exact tablet
  formulation, 30 and 60 mL/min boundaries, monitoring text, exclusions, and fail-closed scope.
- **Resolved — Independent review metadata:** all eight selected exact content versions retain
  `content_version: 1.0.0-draft` as their immutable reviewed version identifier and now record
  `status: reviewed`, `reviewed_content_version: 1.0.0-draft`, Connor Fowler, PharmD as the independent
  qualified clinical-content reviewer, reviewer role, and review date `2026-07-26`.

## Release-gate remediation backlog

The original Day 83 candidate
`73c3fcfd10548db31c2bf6707e73f65c5e7f2eb0` remains a historical release `no-go`.
Work Packages 1-7 completed the bounded software remediation and selected
`179c22842caa45d3a1c5e8c04b0bd83025418545` as the verified software candidate.

The durable record is
`artifacts/verification/full-verification-20260726T023944Z.txt`:

- Pytest: 935 passed, 2 strict XFAILs; exit status 0.
- Ruff: pass; exit status 0.
- CLI walkthrough: all 7 synthetic scenarios verified; exit status 0.
- Overall software verification: **PASS**.
- Later fail-closed implementation, steering-document, and reviewed-content metadata changes mean
  that candidate is no longer the prospective release state.

### Completed remediation

The following previously open remediation work is complete and must not be presented as active:

- integration route and indication coding-system fixture repair;
- strict-XFAIL signal restoration;
- selected-content snapshot policy;
- cefepime golden semantic review;
- Decimal-context assertion correction;
- Ruff baseline selection and remediation;
- complete command and environment capture;
- seven-scenario CLI walkthrough capture;
- placeholder-skip disposition;
- exact candidate selection and Work Package 7 software verification;
- supplied-versus-declared weight-type conflict rejection;
- famotidine adult minimum-weight fail-closed enforcement; and
- exact reviewed status and reviewer metadata for all eight selected clinical-content versions.

### Completed independent review

On 2026-07-26, the project owner confirmed that **Connor Fowler, PharmD** completed the required
independent calculation review, qualified clinical-content review for the selected content set, and
PHI review of the retained evidence for the exact verified candidate.

The selected YAML documents now record the completed qualified review with exact version equality,
reviewer identity, reviewer role, and review date. This metadata makes those exact versions eligible
for software rule matching; it does not authorize direct clinical use or constitute clinical validation.

### Remaining bounded work

1. **Open - Final candidate verification:** select one exact clean post-metadata commit and rerun full
   pytest, Ruff, and CLI capture with no unresolved XFAILs. The retained Work Package 7 artifact does
   not verify the later implementation and content-metadata changes.
2. **Open - Release decision:** complete the final checklist and record an explicit `go` or `no-go` for
   that exact unchanged candidate and its selected content versions. Tag only in a separate bounded
   task after an explicit `go`.

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
