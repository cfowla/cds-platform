# Piperacillin–Tazobactam Clinical-Content Source Selection

> **Prototype only — not for direct clinical use.** This record supports research, education, and
> software development with synthetic or properly de-identified data. It does not authorize
> patient-care use, prescribing, order verification, antimicrobial selection, or autonomous dosing
> decisions.

## 1. Decision status

This document completes the Day 50 source-selection step for the first-slice
piperacillin–tazobactam renal-dose content. It selects one current FDA-approved labeling source for
standard 30-minute infusion regimens and one primary pharmacokinetic/pharmacodynamic source for one
extended-infusion regimen. It defines exact identifiers, supported source contexts, non-dialysis
renal partitions, source limitations, and the independent-review attestations required before any
future content can become eligible for rule matching.

This document is **not** loadable clinical content. It does not create or approve YAML, implement a
rule, select an initial antimicrobial regimen, assess organism susceptibility, or produce a dose
recommendation.

## 2. Selected sources

### 2.1 Standard-infusion governing source

Use the following FDA-approved prescribing information as the governing source for the two initial
standard-infusion content documents:

| Field | Selected value |
|---|---|
| Source ID | `fda_dailymed_piperacillin_tazobactam_wgcc_spl_v14` |
| Evidence source | FDA-approved prescribing information distributed through DailyMed |
| Product | Piperacillin and Tazobactam for Injection, powder for solution, pharmacy bulk package bottles, intravenous use |
| Packager | WG Critical Care, LLC |
| DailyMed set ID | `17a400ae-cbaa-4d07-95f4-c6917dfc0585` |
| DailyMed SPL version | `14` |
| DailyMed record updated | `2026-06-24` |
| DailyMed archive publication date for version 14 | `2026-07-03` |
| Label revision stated in prescribing information | `11/2025` |
| Source sections used | Indications 1.1–1.5; adult dosage 2.1–2.3; warnings 5.5–5.8; renal impairment 8.6 |
| Source URL | <https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=17a400ae-cbaa-4d07-95f4-c6917dfc0585&version=14> |

For the version 1 content schema, use this traceable source-version string unless independent review
requires a different convention:

```text
DailyMed SPL version 14; labeling revised 11/2025; DailyMed record updated 2026-06-24; version 14 published 2026-07-03
```

The proposed schema `publication_date` is `2026-06-24`, preserving the selected DailyMed record
update date consistently with the existing cefepime source convention. The later archive publication
date remains explicit in `source_version`.

The version 1 schema has no `regulatory_label` evidence level. The provisional schema value for this
FDA-approved prescribing information is `guideline`, solely to fit the existing closed enum. Before
any standard-infusion document is marked `reviewed`, the reviewer must approve that mapping or
require a separately scoped schema change.

### 2.2 Extended-infusion governing source

Use the following primary pharmacokinetic/pharmacodynamic publication as the governing source for
one initial extended-infusion document:

| Field | Selected value |
|---|---|
| Source ID | `patel_2010_piperacillin_tazobactam_extended_infusion_renal_adjustment` |
| Evidence level | `primary_literature` |
| Citation | Patel N, Scheetz MH, Drusano GL, Lodise TP. Identification of optimal renal dosage adjustments for traditional and extended-infusion piperacillin-tazobactam dosing regimens in hospitalized patients. Antimicrob Agents Chemother. 2010;54(1):460-465. |
| DOI | `10.1128/AAC.00296-09` |
| PMID | `19858253` |
| PMCID | `PMC2798531` |
| Electronic publication date | `2009-10-26` |
| Issue date | `2010-01` |
| Source context used | Hospitalized-patient population PK model and 9,999-subject Monte Carlo simulations for `3.375 g` every `8 hours` over `4 hours`, including candidate renal adjustment to every `12 hours` at Cockcroft–Gault creatinine clearance less than or equal to `20 mL/min` |
| Source URL | <https://doi.org/10.1128/AAC.00296-09> |

Use the following source-version string:

```text
Antimicrobial Agents and Chemotherapy 54(1):460-465; e-published 2009-10-26; DOI 10.1128/AAC.00296-09
```

The proposed schema `publication_date` is `2009-10-26`, the exact electronic publication date.

This publication is not FDA labeling, not a clinical-outcomes trial, and not a general authorization
for extended infusion. Its renal recommendations are based on population pharmacokinetic modeling
and Monte Carlo probability-of-target-attainment analyses. Future content must preserve that
limitation and remain draft until independently reviewed.

## 3. Frozen supported context

All selected content remains inside the first vertical slice:

- adults aged 18 years or older;
- stable renal function supplied as an explicit case fact;
- unindexed Cockcroft–Gault creatinine clearance in exact `mL/min`;
- no intermittent hemodialysis, peritoneal dialysis, continuous renal replacement therapy, or other
  renal replacement therapy;
- no acute or rapidly changing kidney function;
- exact medication, regimen, source-context indication, route, dose, frequency, and infusion-duration
  matching;
- supplied maintenance-regimen evaluation only, not initial therapy selection, indication
  determination, antimicrobial selection, companion-agent selection, duration-of-therapy advice,
  susceptibility interpretation, or MIC-based treatment selection; and
- total combined piperacillin–tazobactam product dose represented in `g`, not piperacillin-component
  dose.

The initial set intentionally excludes pediatric dosing, dialysis schedules, continuous infusion,
loading doses, `4.5 g` extended-infusion variants, `3.375 g` extended-infusion intervals other than
those defined below, and any standard or extended regimen not explicitly selected in this document.

## 4. Exact identifiers

### 4.1 Shared identifiers

| Dimension | Exact identifier or value |
|---|---|
| `medication.id` | `piperacillin_tazobactam` |
| `route_id` | `iv` |
| Standard-infusion `formulation_id` | `powder_for_solution` |
| Extended-infusion `formulation_id` | `null` pending review because the primary source does not make formulation a regimen dimension |
| Dose unit | `g` of total combined piperacillin–tazobactam product |
| Frequency unit | `hours` |
| Infusion-duration unit | `minutes` |

### 4.2 Source-context indication identifiers

Standard `3.375 g` every `6 hours` content may match only these exact caller-supplied adult indication
identifiers from the selected label:

- `adult_intra_abdominal_infection`
- `adult_skin_and_skin_structure_infection`
- `adult_female_pelvic_infection`
- `adult_moderate_community_acquired_pneumonia`

Standard `4.5 g` every `6 hours` content may match only:

- `adult_nosocomial_pneumonia_initial_presumptive_with_aminoglycoside_context`

The composite nosocomial-pneumonia identifier preserves the source's initial presumptive
aminoglycoside context because the version 1 schema has no separate companion-agent field. The
prototype does not verify or recommend the companion agent; the caller-supplied identifier only
asserts that the source context has already been established outside this workflow.

The extended-infusion content may match only:

- `hospitalized_serious_gram_negative_infection`

This identifier records the publication's hospitalized-patient and serious Gram-negative infection
context. It is not an FDA-labeled indication and does not authorize the prototype to infer an
organism, MIC, severity, or antimicrobial choice.

## 5. Selected exact base regimens

Each row below is one future YAML document and one exact repository key. A case matches only when all
listed dimensions are supplied and exact.

| Regimen ID | Content ID | Rule ID | Base regimen | Supported source-context indication IDs |
|---|---|---|---|---|
| `standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes` | `renal_dose_piperacillin_tazobactam_standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes` | `piperacillin_tazobactam_standard_infusion_iv_3_375_g_every_6_hours_renal_rule` | `3.375 g` IV every `6 hours` over `30 minutes` | `adult_intra_abdominal_infection`; `adult_skin_and_skin_structure_infection`; `adult_female_pelvic_infection`; `adult_moderate_community_acquired_pneumonia` |
| `standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes` | `renal_dose_piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes` | `piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_renal_rule` | `4.5 g` IV every `6 hours` over `30 minutes` | `adult_nosocomial_pneumonia_initial_presumptive_with_aminoglycoside_context` |
| `extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes` | `renal_dose_piperacillin_tazobactam_extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes` | `piperacillin_tazobactam_extended_infusion_iv_3_375_g_every_8_hours_renal_rule` | `3.375 g` IV every `8 hours` over `240 minutes` | `hospitalized_serious_gram_negative_infection` |

The standard source groups multiple labeled indications under one adult regimen. Inclusion means only
that an exact caller-supplied base regimen and source-context indication are eligible for renal
adjustment. The prototype must not choose among indications or initiate therapy.

## 6. Standard-infusion source renal-maintenance matrices

The selected label states that renal adjustment applies at creatinine clearance less than or equal
to `40 mL/min`. Dialysis rows are deliberately omitted because they are outside the frozen first
slice.

### 6.1 Standard `3.375 g` every `6 hours` base regimen

| Source creatinine-clearance band | Maintenance outcome |
|---|---|
| Greater than `40 mL/min` | `3.375 g` every `6 hours` over `30 minutes` |
| `20 to 40 mL/min` | `2.25 g` every `6 hours` over `30 minutes` |
| Less than `20 mL/min` | `2.25 g` every `8 hours` over `30 minutes` |

### 6.2 Standard `4.5 g` every `6 hours` nosocomial-pneumonia base regimen

| Source creatinine-clearance band | Maintenance outcome |
|---|---|
| Greater than `40 mL/min` | `4.5 g` every `6 hours` over `30 minutes` |
| `20 to 40 mL/min` | `3.375 g` every `6 hours` over `30 minutes` |
| Less than `20 mL/min` | `2.25 g` every `6 hours` over `30 minutes` |

### 6.3 Exact continuous partition for unrounded matching

The label's bands define a complete continuous partition without an integer gap. The candidate
version 1 representation is:

| Candidate band ID | Candidate exact interval |
|---|---|
| `below_20` | greater than `0` and less than `20` |
| `20_to_40` | greater than or equal to `20` and less than or equal to `40` |
| `above_40` | greater than `40`, with no upper bound |

Independent review must confirm the positive lower renal-domain boundary and this exact unrounded
representation. The matcher must not round a Cockcroft–Gault value before comparison.

## 7. Extended-infusion source renal-maintenance matrix

The selected primary publication evaluates one extended-infusion parent regimen and supports
waiting to adjust until Cockcroft–Gault creatinine clearance is less than or equal to `20 mL/min`.

| Candidate creatinine-clearance band | Maintenance outcome |
|---|---|
| Greater than `20 mL/min` | `3.375 g` every `8 hours` over `240 minutes` |
| Greater than `0` and less than or equal to `20 mL/min` | `3.375 g` every `12 hours` over `240 minutes` |

The candidate exact ordered partition for future YAML is:

| Candidate band ID | Candidate exact interval |
|---|---|
| `at_or_below_20` | greater than `0` and less than or equal to `20` |
| `above_20` | greater than `20`, with no upper bound |

The paper simulated explicit creatinine-clearance strata and recommends the less-than-or-equal-to
`20 mL/min` adjustment threshold. Applying that statement as a continuous unrounded interval remains
a reviewable clinical-content interpretation.

## 8. Source ambiguities and limitations

1. The standard label uses total grams of combined piperacillin and tazobactam. Future content must
   preserve `g` as total product dose and must not reinterpret it as piperacillin-component dose.
2. The standard selected product is a pharmacy bulk package powder for solution. The initial
   `powder_for_solution` identifier is intentionally broader than package configuration; the reviewer
   must approve that representation or require a narrower identifier.
3. The nosocomial-pneumonia label regimen includes an aminoglycoside context. The version 1 schema
   cannot represent companion medication separately, so the composite indication identifier is a
   provisional fail-closed representation requiring review.
4. The standard label's FDA-approved 30-minute regimens and the extended-infusion publication must
   remain separate source and regimen records. They must not be merged into one generalized dosing
   policy.
5. The extended-infusion regimen is off-label and derived from a population PK model and Monte Carlo
   simulations rather than a randomized clinical-outcomes comparison.
6. The extended-infusion paper's pharmacodynamic target was `50% fT > MIC`; target attainment varied
   by MIC and was suboptimal at `32 mg/L` for all evaluated regimens. The first-slice schema has no
   MIC field and must not generate organism-, MIC-, breakpoint-, or alternative-agent decisions.
7. The publication studied `3.375 g` every `8 hours` over `4 hours` and candidate adjustment to every
   `12 hours`. Do not extrapolate to `4.5 g`, other extended-infusion intervals, continuous infusion,
   or other infusion durations.
8. The extended-infusion source does not make product formulation a dosing dimension. The proposed
   `formulation_id: null` must be reviewed before authoring.
9. Dialysis and other renal-replacement-therapy schedules are outside scope even when present in the
   standard label.
10. Exact monitoring and warning text belongs to Day 51 content authoring and must be sourced rather
    than invented. The label's hematologic, neurologic, renal, and electrolyte warnings must not be
    generalized beyond the selected source.
11. The current DailyMed version is selected explicitly. A future SPL update, manufacturer
    substitution, or source replacement requires a new source-selection decision and content version;
    repositories must not select another label automatically.
12. No source authorizes the prototype to select piperacillin–tazobactam, determine an indication,
    infer renal stability, select companion therapy, or determine duration.

## 9. Required review metadata and attestations

All future piperacillin–tazobactam YAML documents created from this record must remain:

```yaml
review:
  status: "draft"
  reviewed_content_version: null
  reviewer: null
  reviewer_role: null
  reviewed_on: null
```

until an independent clinical-content reviewer is named and completes review. Do not invent or infer
a reviewer identity.

Before changing any document to `reviewed`, record:

- `reviewed_content_version` exactly equal to that document's immutable `content_version`;
- the reviewer's name;
- the reviewer's clinical role and relevant content-review qualification;
- the ISO `YYYY-MM-DD` review date; and
- review notes confirming all of the following:
  - the DailyMed set ID, SPL version, record update date, archive publication date, and stated label
    revision were verified;
  - the Patel publication citation, DOI, dates, population, parent regimen, simulations, and proposed
    adjustment threshold were independently verified;
  - every exact source-context indication and base regimen is supported by its cited source;
  - total combined-product dose units and component-dose interpretation were reviewed;
  - the standard non-dialysis renal matrices were independently checked against the label;
  - the standard and extended continuous unrounded boundary representations were approved or
    replaced with complete, nonoverlapping alternatives;
  - the composite nosocomial-pneumonia identifier and nullable extended-infusion formulation were
    approved or replaced;
  - the `guideline` mapping for FDA-approved labeling and `primary_literature` mapping for the Patel
    publication were approved or the schema was changed;
  - the off-label, modeling, MIC, formulation, and non-outcomes limitations of extended infusion
    remain explicit;
  - pediatric, unstable-renal-function, dialysis, and other renal-replacement-therapy exclusions
    remain explicit;
  - unsupported cases produce no dosing recommendation; and
  - the prototype clinical-use prohibition remains visible.

The author of a YAML change must not treat software validation, schema conformance, or passing tests
as clinical-content approval.

## 10. Day 51 authoring boundary

The next task may encode and test the three exact documents described here. All three must remain
draft until the recorded source, representation, and independent-review requirements are resolved.
Day 51 must not add another piperacillin–tazobactam regimen, generalize the extended-infusion source,
or implement medication-specific engine behavior.
