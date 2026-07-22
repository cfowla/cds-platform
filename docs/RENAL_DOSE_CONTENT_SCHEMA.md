# Renal-Dose Clinical Content Schema

> **Prototype only — not for direct clinical use.** This schema is for research, education,
> and software development with synthetic or properly de-identified data. Content conforming to
> this schema is not clinical instruction and is not approved for patient-care use merely because
> it passes software validation.

## 1. Purpose and authority

This document defines the version 1 YAML contract for renal-dose clinical content in the frozen
first vertical slice. It specifies the document shape, exact identifiers, types, required fields,
renal-boundary semantics, review metadata, and validation invariants that later typed models and
repository implementations must enforce.

The project charter remains authoritative for scope and safety. The first vertical slice limits
content to cefepime, piperacillin–tazobactam, and famotidine. The renal calculator specification
governs the unrounded Cockcroft–Gault value supplied to band matching. This schema does not select
clinical sources or define medication-specific doses, regimens, indications, or renal cutoffs.

## 2. Document unit and matching key

One YAML document represents one exact medication-and-regimen pair at one content version. Its
repository lookup key is the tuple:

```text
(medication.id, regimen.id, content_version)
```

The current version is selected by repository policy, not by the content document. Aliases,
case folding, whitespace normalization, fuzzy matching, and fallback from one regimen to another
are prohibited.

The only permitted first-slice medication identifiers are these exact, case-sensitive strings:

| Medication | `medication.id` |
|---|---|
| Cefepime | `cefepime` |
| Piperacillin–tazobactam | `piperacillin_tazobactam` |
| Famotidine | `famotidine` |

Every `regimen.id`, `rule_id`, source ID, indication ID, route ID, and formulation ID is also an
exact identifier. Identifiers must match `^[a-z][a-z0-9_]*$`. Medication-specific regimen values
are established only after source selection and clinical-content review; this schema does not
invent them.

## 3. Scalar and collection conventions

- All mappings reject unknown keys.
- All required keys must be present; an empty string never means missing.
- Identifiers, versions, dates, units, citations, URLs, and narrative text are YAML strings.
- Clinical decimal values are quoted base-10 strings matching
  `^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$`; YAML integer or floating-point nodes are invalid for
  those fields.
- Calendar dates use quoted ISO 8601 `YYYY-MM-DD` strings.
- Lists preserve source order, contain no duplicate identifiers, and must meet the minimum
  cardinality stated below.
- `null` is permitted only where this contract explicitly allows it.
- Units are exact, case-sensitive strings. No unit inference, normalization, or conversion occurs
  while loading or matching content.
- A missing numeric value is `null` only when expressly allowed; zero is always a real value.

## 4. Normative YAML shape

The following is a structural template, not valid clinical content. Angle-bracket values are
non-loadable placeholders and must never be committed as a content fixture.

```yaml
schema_version: "1"
content_id: "<exact_identifier>"
content_version: "<version_string>"
rule_id: "<exact_identifier>"
medication:
  id: "<cefepime|piperacillin_tazobactam|famotidine>"
  display: "<nonempty_text>"
regimen:
  id: "<exact_identifier>"
  display: "<nonempty_text>"
  indication_ids:
    - "<exact_identifier>"
  route_id: "<exact_identifier>"
  formulation_id: "<exact_identifier_or_null>"
  base_dose:
    value: "<decimal_string>"
    unit: "<exact_unit>"
  frequency_interval:
    value: "<positive_decimal_string>"
    unit: "<exact_time_unit>"
  infusion_duration:
    value: "<positive_decimal_string>"
    unit: "<exact_time_unit>"
supported_context:
  minimum_age_years: 18
  renal_method: "cockcroft_gault"
  renal_unit: "mL/min"
  renal_function_stable: true
  renal_replacement_therapy: false
  limitations:
    - "<nonempty_text>"
renal_domain:
  lower:
    value: "<decimal_string>"
    inclusive: false
  upper: null
renal_bands:
  - id: "<exact_identifier>"
    lower:
      value: "<decimal_string>"
      inclusive: true
    upper:
      value: "<decimal_string>"
      inclusive: false
    outcome: "recommendation"
    recommendation:
      action: "<continue|adjust_dose|hold|stop|avoid|monitor|switch|clarify|none>"
      dose:
        value: "<decimal_string>"
        unit: "<exact_unit>"
      route_id: "<exact_identifier>"
      frequency_interval:
        value: "<positive_decimal_string>"
        unit: "<exact_time_unit>"
      infusion_duration:
        value: "<positive_decimal_string>"
        unit: "<exact_time_unit>"
      rationale: "<nonempty_text>"
      monitoring:
        - "<nonempty_text>"
    no_recommendation_reason: null
    source_ids:
      - "<exact_identifier>"
    limitations:
      - "<nonempty_text>"
sources:
  - id: "<exact_identifier>"
    evidence_level: "<guideline|primary_literature|local_policy|expert_opinion>"
    citation: "<nonempty_text>"
    source_document: "<nonempty_text>"
    source_version: "<nonempty_text>"
    publication_date: "<YYYY-MM-DD_or_null>"
    url: "<absolute_https_url_or_null>"
review:
  status: "draft"
  reviewed_content_version: null
  reviewer: null
  reviewer_role: null
  reviewed_on: null
  notes: "<nonempty_text_or_null>"
limitations:
  - "<nonempty_text>"
```

`formulation_id`, `infusion_duration`, `publication_date`, and `url` are nullable only when the
source or supported regimen genuinely does not define or require that fact. A missing fact may
not be converted to `null` merely to make partial content loadable. Medication-specific
validation may make a nullable schema field required for an exact supported regimen.

## 5. Top-level fields

| Field | Type | Required | Contract |
|---|---|---:|---|
| `schema_version` | string | yes | Exactly `"1"` for this contract. |
| `content_id` | identifier | yes | Stable identifier unique across renal-dose documents. |
| `content_version` | string | yes | Nonempty immutable version for this complete document. |
| `rule_id` | identifier | yes | Stable rule identifier retained in every matched result. |
| `medication` | mapping | yes | Exact medication identity; no aliases. |
| `regimen` | mapping | yes | One exact supported base regimen. |
| `supported_context` | mapping | yes | First-slice population and renal-method constraints. |
| `renal_domain` | interval | yes | Exact domain partitioned by `renal_bands`. |
| `renal_bands` | list | yes | One or more ordered, reachable bands. |
| `sources` | list | yes | One or more source records referenced by every band. |
| `review` | mapping | yes | Explicit approval state and reviewer metadata. |
| `limitations` | list | yes | One or more document-level limitations. |

`content_id` must equal `renal_dose_<medication.id>_<regimen.id>`. A new content version retains
the same `content_id`; changing medication or regimen identity creates a different document.

## 6. Regimen and supported-context contract

`regimen` contains the exact context that must match before renal-band evaluation:

- `id` and `display` are required nonempty strings.
- `indication_ids` contains one or more exact supported indication identifiers.
- `route_id` is required.
- `formulation_id` is either an exact identifier or `null` only when formulation is not a source-
  defined matching dimension.
- `base_dose` and `frequency_interval` are required quantities.
- `infusion_duration` is a quantity or `null`; it becomes required whenever infusion strategy is
  a source-defined regimen dimension.

`supported_context` is fixed for the first slice:

- `minimum_age_years` is the YAML integer `18`;
- `renal_method` is exactly `cockcroft_gault`;
- `renal_unit` is exactly `mL/min`;
- `renal_function_stable` is exactly `true`;
- `renal_replacement_therapy` is exactly `false`; and
- `limitations` contains at least one nonempty statement of important population or workflow
  exclusions.

The loader must reject content that silently broadens this context. Matching code must receive
validated typed facts and must not infer missing indication, route, formulation, dose, frequency,
or infusion duration.

## 7. Quantity contract

Each quantity is a closed mapping with exactly:

- `value`: a quoted decimal string; and
- `unit`: a nonempty exact unit string.

Dose values must be greater than zero when a dose is present. Frequency intervals and infusion
durations must be greater than zero. No quantity may be represented as a combined free-text value
such as `"2 g"`. The schema defines no conversion table and does not declare two units equivalent.

## 8. Renal interval and boundary semantics

An interval has `lower` and `upper` endpoints. Each endpoint is either:

```yaml
value: "<decimal_string>"
inclusive: <true|false>
```

or `null`, meaning unbounded in that direction. A null endpoint has no inclusivity flag.

The matched renal value is the stored, unquantized `Decimal` Cockcroft–Gault result in exact
`mL/min`. It is never a presentation-rounded value. An endpoint comparison is:

```text
lower satisfied = lower is null
               or value > lower.value
               or (lower.inclusive and value == lower.value)

upper satisfied = upper is null
               or value < upper.value
               or (upper.inclusive and value == upper.value)
```

A band matches only when both comparisons are true. The rule engine must never round,
interpolate, extrapolate, or choose the nearest band.

`renal_domain` declares the complete renal interval addressed by the document. `renal_bands`
must form one exact partition of that domain:

- bands are ordered from lowest to highest renal value;
- every band lies wholly within `renal_domain`;
- every band is nonempty and reachable;
- adjacent bands have equal shared endpoint values;
- at a shared endpoint, exactly one adjacent band is inclusive;
- no value in the domain matches zero bands (gap) or more than one band (overlap); and
- the first and last band boundaries exactly reproduce the domain boundaries.

An intentionally matched interval that must produce no dose recommendation is represented by a
band with `outcome: no_recommendation`; it is not represented by omitting a band and creating a
gap.

## 9. Band outcome contract

Every band has a unique `id`, at least one `source_id`, and one of two outcomes.

### `outcome: recommendation`

- `recommendation` is required.
- `no_recommendation_reason` is `null`.
- `action` must be one implemented `RecommendationAction` wire value other than `unknown`.
- `dose`, `route_id`, `frequency_interval`, and `rationale` are required for `continue` and
  `adjust_dose`.
- `infusion_duration` is required when the regimen's infusion strategy is a matching dimension;
  otherwise it may be `null`.
- `monitoring` is a list of nonempty strings and may be empty.

### `outcome: no_recommendation`

- `recommendation` is `null`.
- `no_recommendation_reason` is required nonempty text.
- The matched result must fail closed and contain no `DoseRecommendation`.

Band-level `limitations` may be empty, but must contain only nonempty strings when present.

## 10. Evidence, review, and versioning

Every document contains one or more `sources`. Source IDs are unique within the document, and
every `renal_bands[*].source_ids` entry must resolve to one of them. Each source requires an
implemented non-`unknown` `EvidenceLevel`, a nonempty citation, source document, and source
version. `publication_date` may be `null` only when the source has no applicable publication date.
`url` may be `null`; when present it must be an absolute HTTPS URL.

`review.status` is exactly one of `draft`, `reviewed`, or `retired`.

- `draft`: not eligible for rule matching. `reviewed_content_version` and reviewer fields are
  `null`.
- `reviewed`: eligible only if `reviewed_content_version` exactly equals the document's immutable
  `content_version` and `reviewer`, `reviewer_role`, and `reviewed_on` are nonempty.
- `retired`: not eligible for rule matching and retained only for audit or rollback policy.

The repository must never treat `draft` or `retired` content as reviewed. Passing structural
validation does not change approval status. Later supersession and version-selection policy is
outside this schema task.

## 11. Required validation failures

The future schema validator must reject, at minimum:

- missing required keys, unknown keys, wrong node types, empty required strings, or duplicate IDs;
- unsupported medication IDs, malformed exact identifiers, or inconsistent `content_id`;
- unsupported schema version or empty content version;
- non-string clinical decimals, invalid decimal syntax, nonpositive required quantities, or
  missing units;
- unsupported first-slice renal method, renal unit, population, stability, or renal-replacement-
  therapy declarations;
- empty, reversed, unreachable, unsorted, gapped, or overlapping renal bands;
- shared boundaries included by both adjacent bands or excluded by both adjacent bands;
- a band outside the declared renal domain;
- outcome/recommendation contradictions or incomplete dose recommendations;
- unresolved source references or missing source and review metadata;
- a `reviewed` document with incomplete reviewer fields; and
- placeholders, fabricated defaults, or clinical fields set to `null` when the exact regimen
  requires them.

These are content errors, not expected patient-data gaps. They must prevent the document from
being returned as usable content and must never be resolved by silently selecting a band or
recommendation.

## 12. Component boundary and deferred decisions

- YAML loading, parsing, and schema validation belong in the repository layer.
- Repositories return future typed content objects; services and rules do not read YAML.
- Rule matching receives validated typed content and the unrounded renal value.
- Content documents contain data only and execute no logic.
- This task adds no YAML dependency, parser, validator, repository, matcher, medication fixture,
  dose recommendation, or user interface.
- Medication-specific regimen IDs, indications, formulations, doses, infusion strategies, renal
  bands, sources, reviewer identity, and limitations remain unresolved until their scheduled
  source-selection and content-authoring tasks.
