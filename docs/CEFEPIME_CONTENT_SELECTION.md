# Cefepime Clinical-Content Source Selection

> **Prototype only — not for direct clinical use.** This record supports research, education, and
> software development with synthetic or properly de-identified data. It does not authorize
> patient-care use, prescribing, order verification, or autonomous dosing decisions.

## 1. Decision status

This document completes the Day 43 source-selection step for the first-slice cefepime renal-dose
content. It selects one authoritative labeling source, defines the exact initial identifiers and
supported base regimens, records the source renal-maintenance matrix, and identifies ambiguities
that must be resolved during independent clinical-content review.

This document is **not** loadable clinical content. It does not mark any YAML document as reviewed,
does not make the existing synthetic fixture clinically usable, and does not implement rule
matching or a dose recommendation.

## 2. Selected authoritative source

Use the following FDA-approved prescribing information as the governing source for the initial
cefepime content set:

| Field | Selected value |
|---|---|
| Source ID | `fda_dailymed_cefepime_for_injection_wgcc_spl_v17` |
| Evidence source | FDA-approved prescribing information distributed through DailyMed |
| Product | Cefepime for Injection, USP, powder for solution, intravenous or intramuscular use |
| Packager | WG Critical Care, LLC |
| DailyMed set ID | `5fd857e5-591f-44ca-80cf-fd903660b03c` |
| DailyMed SPL version | `17` |
| DailyMed record updated | `2026-06-23` |
| Label revision stated in prescribing information | `10/2022` |
| Source sections used | Indications 1.1–1.5; adult dosage 2.1; renal impairment 2.3; neurotoxicity 5.2; renal impairment 8.6 |
| Source URL | <https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=5fd857e5-591f-44ca-80cf-fd903660b03c&version=17> |

For the version 1 content schema, use this traceable source-version string unless review requires a
more specific convention:

```text
DailyMed SPL version 17; labeling revised 10/2022; DailyMed record updated 2026-06-23
```

The proposed `publication_date` is `2026-06-23`, representing the selected DailyMed SPL record
update date. The label-revision month remains preserved in `source_version` because the source does
not state a full calendar date for the October 2022 clinical-label revision.

### Evidence-level representation

The schema currently has no `regulatory_label` evidence level. The provisional schema value for
this FDA-approved prescribing information is `guideline`, solely to fit the existing closed enum.
Before any cefepime document is marked `reviewed`, the reviewer must explicitly approve this
mapping or require a separately scoped schema change. The source must not be described as primary
literature, local policy, or expert opinion.

## 3. Frozen supported context

The selected content remains inside the first vertical slice:

- adults aged 18 years or older;
- stable renal function supplied as an explicit case fact;
- unindexed Cockcroft–Gault creatinine clearance in exact `mL/min`;
- no intermittent hemodialysis, peritoneal dialysis, continuous renal replacement therapy, or other
  renal replacement therapy;
- no acute or rapidly changing kidney function;
- exact medication, regimen, indication, route, formulation, dose, frequency, and infusion-duration
  matching;
- maintenance-regimen evaluation only, not initial therapy selection, loading-dose selection,
  antimicrobial selection, or duration-of-therapy advice; and
- intravenous powder-for-solution regimens administered over approximately 30 minutes.

The initial content set intentionally excludes pediatric dosing, intramuscular dosing, premixed or
frozen-container formulation restrictions, off-label extended infusions, continuous infusions, and
any regimen not represented by one of the four maintenance-schedule columns in the selected source.

## 4. Exact identifiers

### Shared identifiers

| Dimension | Exact identifier |
|---|---|
| `medication.id` | `cefepime` |
| `route_id` | `iv` |
| `formulation_id` | `powder_for_solution` |
| Infusion duration | value `30`, unit `minutes` |

### Indication identifiers

- `moderate_severe_pneumonia`
- `pseudomonas_aeruginosa_moderate_severe_pneumonia`
- `empiric_febrile_neutropenia`
- `mild_moderate_uncomplicated_or_complicated_uti`
- `severe_uncomplicated_or_complicated_uti`
- `moderate_severe_uncomplicated_skin_structure_infection`
- `complicated_intra_abdominal_infection_with_metronidazole`
- `pseudomonas_aeruginosa_complicated_intra_abdominal_infection_with_metronidazole`

Pathogen-qualified indication identifiers are required because the source specifically directs
`2 g` every `8 hours` for *Pseudomonas aeruginosa* in the source rows carrying that footnote, while
the version 1 schema has no separate organism-matching field.

## 5. Selected exact base regimens

Each row below is one future YAML document and one exact repository key. A case matches only when
all listed regimen dimensions are supplied and exact.

| Regimen ID | Content ID | Rule ID | Base regimen | Supported indication IDs |
|---|---|---|---|---|
| `iv_500_mg_every_12_hours_over_30_minutes` | `renal_dose_cefepime_iv_500_mg_every_12_hours_over_30_minutes` | `cefepime_iv_500_mg_every_12_hours_renal_rule` | `500 mg` IV every `12 hours` over `30 minutes` | `mild_moderate_uncomplicated_or_complicated_uti` |
| `iv_1_g_every_12_hours_over_30_minutes` | `renal_dose_cefepime_iv_1_g_every_12_hours_over_30_minutes` | `cefepime_iv_1_g_every_12_hours_renal_rule` | `1 g` IV every `12 hours` over `30 minutes` | `mild_moderate_uncomplicated_or_complicated_uti`; `moderate_severe_pneumonia` |
| `iv_2_g_every_12_hours_over_30_minutes` | `renal_dose_cefepime_iv_2_g_every_12_hours_over_30_minutes` | `cefepime_iv_2_g_every_12_hours_renal_rule` | `2 g` IV every `12 hours` over `30 minutes` | `moderate_severe_pneumonia`; `severe_uncomplicated_or_complicated_uti`; `moderate_severe_uncomplicated_skin_structure_infection`; `complicated_intra_abdominal_infection_with_metronidazole` |
| `iv_2_g_every_8_hours_over_30_minutes` | `renal_dose_cefepime_iv_2_g_every_8_hours_over_30_minutes` | `cefepime_iv_2_g_every_8_hours_renal_rule` | `2 g` IV every `8 hours` over `30 minutes` | `moderate_severe_pneumonia`; `pseudomonas_aeruginosa_moderate_severe_pneumonia`; `empiric_febrile_neutropenia`; `complicated_intra_abdominal_infection_with_metronidazole`; `pseudomonas_aeruginosa_complicated_intra_abdominal_infection_with_metronidazole` |

The selected source presents ranges for some indications. Inclusion here means only that the exact
caller-supplied base regimen is one of the source-listed schedules and has a corresponding renal
maintenance column. The prototype must not choose among source-listed doses or frequencies.

## 6. Source renal-maintenance matrix

The following values are transcribed from the selected source's adult renal-impairment maintenance
schedule. Dialysis rows are deliberately omitted because they are outside the frozen first slice.

| Source creatinine-clearance band | `500 mg every 12 hours` base | `1 g every 12 hours` base | `2 g every 12 hours` base | `2 g every 8 hours` base |
|---|---|---|---|---|
| Greater than `60 mL/min` | `500 mg` every `12 hours` | `1 g` every `12 hours` | `2 g` every `12 hours` | `2 g` every `8 hours` |
| `30 to 60 mL/min` | `500 mg` every `24 hours` | `1 g` every `24 hours` | `2 g` every `24 hours` | `2 g` every `12 hours` |
| `11 to 29 mL/min` | `500 mg` every `24 hours` | `500 mg` every `24 hours` | `1 g` every `24 hours` | `2 g` every `24 hours` |
| Less than `11 mL/min` | `250 mg` every `24 hours` | `250 mg` every `24 hours` | `500 mg` every `24 hours` | `1 g` every `24 hours` |

The selected source states that dosage adjustment applies at creatinine clearance less than or equal
to `60 mL/min` and that Cockcroft–Gault estimation assumes serum creatinine represents steady-state
renal function.

## 7. Boundary interpretation requiring review

The source prints integer-labeled bands, but the platform matches an unrounded `Decimal` value.
Literal transcription of `11 to 29` would leave values such as `29.5 mL/min` unmatched. The
candidate continuous partition for independent review is:

| Candidate band ID | Candidate exact interval |
|---|---|
| `below_11` | greater than `0` and less than `11` |
| `11_to_below_30` | greater than or equal to `11` and less than `30` |
| `30_to_60` | greater than or equal to `30` and less than or equal to `60` |
| `above_60` | greater than `60`, with no upper bound |

This candidate preserves the source's apparent integer threshold semantics and creates a complete,
nonoverlapping continuous domain. It remains an interpretation, not a source quote. It must be
explicitly approved before the renal bands are marked reviewed. The matcher must use the stored
unquantized Cockcroft–Gault value and must not round to an integer before comparison.

## 8. Additional source ambiguities and limitations

1. The source provides dose and frequency ranges for some indications but does not define how to
   select one exact base regimen within each range. The first slice therefore adjusts only a fully
   supplied exact regimen and never selects the initial regimen.
2. The source uses both `mg` and `g`. Future YAML must preserve the displayed source unit for each
   quantity unless an explicit, reviewed canonical-unit policy is added; the loader and matcher must
   not perform hidden unit conversion.
3. The source states IV administration over approximately 30 minutes. The initial exact matching
   value is `30 minutes`; the reviewer must confirm that this representation is acceptable for the
   source word “approximately.”
4. The source includes IM treatment for a narrow UTI context, but IM is excluded from this initial
   content set.
5. CAPD and hemodialysis schedules are present in the source but are excluded by the first-slice
   renal-replacement-therapy boundary.
6. Neurotoxicity risk is emphasized in renal impairment, especially with unadjusted dosing. Exact
   monitoring and warning text belongs to the Day 44 content-authoring and review step and must be
   sourced rather than invented.
7. The source URL identifies one current manufacturer SPL. Future source replacement or
   supplementation requires a new source-selection decision and content version; repositories must
   not silently substitute another label.

## 9. Required review metadata and attestations

All future cefepime YAML documents created from this record must remain:

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

Before changing `status` to `reviewed`, every document must record:

- `reviewed_content_version` exactly equal to that document's immutable `content_version`;
- the reviewer's name;
- the reviewer's clinical role and relevant content-review qualification;
- the ISO `YYYY-MM-DD` review date; and
- review notes confirming all of the following:
  - the selected SPL set ID, version, update date, and stated label revision were verified;
  - each exact indication and base regimen is supported by the cited source;
  - the renal-maintenance matrix was independently checked against the source;
  - the continuous boundary interpretation was approved or replaced with another complete,
    nonoverlapping interpretation;
  - the provisional `guideline` evidence-level mapping was approved or the schema was changed;
  - source units and the approximately 30-minute infusion representation were reviewed;
  - pediatric, unstable-renal-function, and renal-replacement-therapy exclusions remain explicit;
  - unsupported cases produce no dosing recommendation; and
  - the prototype clinical-use prohibition remains visible.

The author of the YAML change must not treat software validation, schema conformance, or passing
tests as clinical-content approval.

## 10. Day 44 authoring boundary

The next task may encode the four exact documents described here, but they must remain draft until
the unresolved review decisions and reviewer metadata are completed. The existing
`cefepime_synthetic_fixture.yaml` remains an invented structural fixture and must not be edited into
clinical content or used as the source document.
