# Famotidine Clinical-Content Source Selection

> **Prototype only — not for direct clinical use.** This record supports research, education, and
> software development with synthetic or properly de-identified data. It does not authorize
> patient-care use, prescribing, order verification, treatment selection, or autonomous dosing
> decisions.

## 1. Decision status

This document completes the Day 53 source-selection step for first-slice famotidine renal-dose
content. It selects one current FDA-approved prescribing-information source, defines one exact oral
maintenance regimen and source-context indication, records the non-dialysis renal thresholds, and
states the limitations and independent-review attestations required before future content can become
eligible for rule matching.

This document is **not** loadable clinical content. It does not create or approve YAML, implement a
rule, select therapy, diagnose an indication, or produce a dose recommendation.

## 2. Selected governing source

Use the following FDA-approved prescribing information as the governing source for the initial
famotidine document:

| Field | Selected value |
|---|---|
| Source ID | `fda_dailymed_famotidine_sportpharm_spl_v1` |
| Evidence source | FDA-approved prescribing information distributed through DailyMed |
| Product | Famotidine tablets, film coated, 20 mg and 40 mg, for oral use |
| Packager | Sportpharm LLC |
| Label status | Repackaged label; source NDCs identify the underlying labeled product |
| DailyMed set ID | `4421ceb7-a114-436c-871a-7bc5444f8154` |
| DailyMed SPL version | `1` |
| DailyMed record updated | `2026-06-26` |
| Label revision stated in prescribing information | `06/2026` |
| Source sections used | Adult indications 1; dosage 2.1; renal dosage 2.2; administration 2.3; warnings 5.1; renal impairment 8.6 |
| Source URL | <https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=4421ceb7-a114-436c-871a-7bc5444f8154&version=1> |

Use this source-version string unless independent review requires another convention:

```text
DailyMed SPL version 1; labeling revised 06/2026; DailyMed record updated 2026-06-26
```

The proposed schema `publication_date` is `2026-06-26`, preserving the DailyMed record update date.
The version 1 schema has no `regulatory_label` evidence level. The provisional evidence level is
`guideline`, solely to fit the existing closed enum. Independent review must approve that mapping or
require a separately scoped schema change.

## 3. Frozen supported context

The initial famotidine content remains inside the first vertical slice:

- adults aged 18 years or older;
- stable renal function supplied as an explicit case fact;
- unindexed Cockcroft–Gault creatinine clearance in exact `mL/min`;
- no intermittent hemodialysis, peritoneal dialysis, continuous renal replacement therapy, or other
  renal replacement therapy;
- exact medication, source-context indication, route, formulation, dose, frequency, and content
  version matching;
- supplied maintenance-regimen evaluation only, not diagnosis, treatment selection, duration advice,
  deprescribing, prophylaxis selection, or symptom assessment; and
- oral tablet dosing represented in `mg` with frequency intervals represented in `hours`.

The initial document intentionally excludes pediatric use, patients weighing less than 40 kg,
pregnancy or lactation, unstable renal function, renal replacement therapy, oral suspension, 10 mg
formulations, intravenous famotidine, active ulcer treatment, erosive esophagitis, pathological
hypersecretory conditions, and every regimen not explicitly selected below.

## 4. Exact identifiers and base regimen

| Dimension | Exact identifier or value |
|---|---|
| `medication.id` | `famotidine` |
| `indication_id` | `adult_symptomatic_nonerosive_gerd` |
| `route_id` | `po` |
| `formulation_id` | `film_coated_tablet` |
| Dose unit | `mg` |
| Frequency unit | `hours` |
| Base dose | `20 mg` |
| Base frequency | every `12 hours` |
| Infusion duration | `null` |
| Regimen ID | `oral_film_coated_tablet_20_mg_every_12_hours` |
| Content ID | `renal_dose_famotidine_oral_film_coated_tablet_20_mg_every_12_hours` |
| Rule ID | `famotidine_oral_film_coated_tablet_20_mg_every_12_hours_renal_rule` |

The caller must supply the exact source-context indication. The prototype must not infer GERD from
symptoms, diagnoses, medications, or prior orders.

## 5. Selected renal-maintenance matrix

The selected label gives `20 mg` twice daily for symptomatic nonerosive GERD with normal renal
function and recommends the following maximum doses when creatinine clearance is below `60 mL/min`:

| Source creatinine-clearance band | Maintenance outcome |
|---|---|
| Greater than or equal to `60 mL/min` | `20 mg` every `12 hours` |
| `30 to 60 mL/min` | `20 mg` every `24 hours` |
| Less than `30 mL/min` | `20 mg` every `48 hours` |

The label also notes an alternate `10 mg` once-daily regimen for the severe-impairment row using an
alternate formulation. That alternate is outside the selected tablet-strength and formulation scope
and must not be emitted by the initial content.

For continuous matching against unrounded values, the candidate complete partition is:

| Candidate band ID | Candidate exact interval |
|---|---|
| `below_30` | greater than `0` and less than `30` |
| `30_to_below_60` | greater than or equal to `30` and less than `60` |
| `at_or_above_60` | greater than or equal to `60`, with no upper bound |

The source table labels the middle row `30 to 60 mL/minute`, while section 8.6 states that no dosage
adjustment is needed at creatinine clearance greater than or equal to `60 mL/minute`. The candidate
partition therefore assigns exactly `60` to the no-adjustment band. This reconciliation is a
reviewable clinical-content interpretation; the matcher must not round before comparison.

## 6. Source ambiguities and limitations

1. The selected DailyMed record is a current repackaged FDA-approved label. Independent review must
   confirm that this source is acceptable or select and version the underlying manufacturer label.
2. The renal table describes recommended **maximum** dosages. Future content must preserve that
   limitation and must not imply that the prototype selected an initial dose or established need.
3. Exactly `60 mL/min` is assigned to the no-adjustment band based on section 8.6 despite the table's
   compact `30 to 60` heading. That boundary must be independently approved or replaced with a
   complete nonoverlapping interpretation.
4. The alternate `10 mg` regimen requires another formulation and is unsupported. Do not convert,
   split, or infer tablet strengths.
5. The source warns of CNS adverse reactions and prolonged QT intervals in moderate and severe renal
   impairment. Exact warning and monitoring text belongs to Day 54 content authoring and must be
   sourced rather than generalized.
6. Oral suspension, intravenous products, pathological hypersecretory conditions, erosive
   esophagitis, ulcer treatment, and recurrence prevention have different regimen matrices and remain
   unsupported.
7. The current source version is selected explicitly. A future SPL update, manufacturer substitution,
   or source replacement requires a new source-selection decision and content version; repositories
   must not select another label automatically.
8. No source authorizes the prototype to diagnose GERD, select famotidine, determine duration,
   evaluate interactions or contraindications, infer renal stability, or act autonomously.

## 7. Required review metadata and attestations

Any future famotidine YAML document created from this record must remain:

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

Before changing a document to `reviewed`, record:

- `reviewed_content_version` exactly equal to the immutable `content_version`;
- the reviewer's name, clinical role, relevant qualification, and ISO `YYYY-MM-DD` review date; and
- review notes confirming that:
  - the DailyMed set ID, SPL version, update date, stated revision, packager, and repackaged-label
    status were verified;
  - the exact indication, route, formulation, base regimen, dose units, and frequency units are
    supported by the selected source;
  - the normal, moderate, and severe renal outcomes were independently checked;
  - the continuous unrounded interpretation at `30` and `60 mL/min` was approved or replaced with a
    complete, nonoverlapping alternative;
  - the `guideline` mapping for FDA-approved labeling was approved or the schema was changed;
  - the maximum-dose, alternate-formulation, CNS, QT, pediatric, unstable-renal-function, and
    renal-replacement-therapy limitations remain explicit;
  - unsupported cases produce no dosing recommendation; and
  - the prototype clinical-use prohibition remains visible.

Software validation, schema conformance, or passing tests do not confer clinical-content approval.

## 8. Day 54 authoring boundary

The next task may encode and test only the exact famotidine document described here. It must remain
`draft` until the source, boundary representation, and independent-review requirements are resolved.
Day 54 must not add another famotidine indication, formulation, route, regimen, or medication-specific
engine behavior.
