# Clinical-Content Workflow

This document defines the controlled lifecycle for renal-dose clinical content in the CDS Platform.
It describes how source material becomes an inspectable, versioned content document and how that
content may become eligible for prototype rule matching.

`PROJECT_CHARTER.md` remains authoritative for safety, scope, and change control.
`FIRST_VERTICAL_SLICE.md` defines the supported renal workflow. This prototype is for research,
education, and software development only; it is not for direct clinical use and must use synthetic
or properly de-identified data.

## Scope

This workflow applies only to versioned renal-dose content for the first vertical slice:

- cefepime;
- piperacillin-tazobactam; and
- famotidine.

It does not authorize new medications, populations, renal methods, settings, regimens, interfaces,
or clinical uses. Any such expansion requires a separately approved scope change before content is
created or reviewed.

## Implemented content contract

The current implementation establishes these non-negotiable boundaries:

1. YAML is parsed and validated only in the repository layer.
2. The schema is closed: missing keys, unknown keys, duplicate YAML keys, invalid identifiers,
   unsupported units, malformed intervals, gaps, overlaps, contradictions, unresolved source links,
   and incomplete review metadata are rejected.
3. Medication, regimen, units, rule identifiers, and content versions are exact and case-sensitive.
   They are not normalized, inferred, aliased, fuzzy-matched, or selected by fallback.
4. Content is retrieved by the exact
   `(medication_id, regimen_id, content_version)` key supplied by the caller.
5. The YAML repository reads only explicitly supplied paths. It performs no directory discovery,
   automatic version selection, or review-status filtering.
6. Rule matching permits a recommendation only when review status is `reviewed`, the recorded
   reviewed version exactly equals the document version, and reviewer name, role, and date are
   present.
7. `draft` and `retired` content are not eligible for a recommendation. The matcher fails closed and
   returns no dose recommendation.

Software tests establish consistency with the encoded contract. They do not establish clinical
validity, production readiness, or authorization for patient-care use.

## Roles and separation of duties

One person may perform more than one software role, but independent clinical verification must not
be represented as complete unless a qualified reviewer independently evaluates the content.

### Content author

The content author selects in-scope sources, extracts source facts, records ambiguities, creates the
YAML document, and prepares traceable tests. The author must not mark personal self-review as
independent verification.

### Independent clinical-content reviewer

The reviewer evaluates the source-to-content translation, clinical boundaries, regimen context,
recommendations, limitations, citations, and golden cases. The reviewer must be identifiable by
name and role in the reviewed content metadata.

### Software reviewer

The software reviewer verifies schema conformance, deterministic behavior, exact matching,
fail-closed outcomes, test coverage, and serialized audit fields. Software review does not replace
clinical-content review.

### Release custodian

The release custodian records which exact reviewed content version is intended for a prototype
release or reproducible test run. The current prototype has no automatic active-version registry;
version selection remains explicit.

## Lifecycle states

The schema supports exactly three review states.

### `draft`

- Content is being authored, corrected, or reviewed.
- Reviewer, reviewer role, review date, and reviewed-content-version fields must be `null`.
- Draft content may be schema-valid and testable, but it is not eligible for a recommendation.
- Unresolved ambiguity, missing review, or incomplete independent verification keeps content in this
  state.

### `reviewed`

- Independent review is complete for the exact document version.
- `reviewed_content_version` exactly equals `content_version`.
- Reviewer name, reviewer role, and review date are present.
- Content may be eligible for prototype rule matching only when the exact version is requested and
  all software, schema, context, and rule checks also pass.
- Reviewed status does not authorize direct clinical use.

### `retired`

- The document is intentionally ineligible for new recommendations.
- Review metadata may be complete or entirely `null`, as required by the current schema.
- Retired content may remain in repository history for auditability, but the matcher produces no
  recommendation from it.

“Superseded” is a release relationship, not a fourth schema status. A reviewed version may be
superseded by another reviewed version while remaining available for explicit rollback. It becomes
`retired` only when it should no longer be eligible for any new evaluation.

## Controlled workflow

### 1. Confirm scope before selecting content

Before extraction begins, confirm that the proposed document stays within the charter and first
vertical slice. Record, rather than silently resolve, any request involving an unsupported
medication, regimen, formulation, route, indication, population, renal method, unstable renal
function, or renal replacement therapy.

A scope question blocks content authoring as eligible content. It belongs in a separately bounded
change proposal or `BACKLOG.md`, not in an opportunistic content expansion.

### 2. Select authoritative sources

Select sources that directly support the exact medication, regimen, population, renal method, renal
bands, and recommendation represented by the document.

Source selection must:

- prefer current authoritative prescribing information, guidelines, or applicable institutional
  policy over uncited secondary summaries;
- preserve the exact source document, source version, and publication date when available;
- distinguish guideline, primary-literature, local-policy, and expert-opinion evidence;
- identify material conflicts, gaps, or ambiguity among sources;
- avoid extrapolating from a different formulation, indication, route, infusion strategy,
  population, or renal method; and
- use stable citations or HTTPS links when available.

A source conflict is not resolved by silently choosing the more convenient value. The document
remains draft until the conflict is explicitly resolved, limited, or excluded from scope.

### 3. Extract into the schema

Translate the selected source into one content document for one exact medication, regimen, and
content version. Preserve:

- exact medication, regimen, indication, route, and formulation identifiers;
- base dose, frequency, and infusion duration with explicit units;
- adult population and supported renal context;
- the complete renal domain and every boundary's inclusivity;
- one explicit outcome for each band;
- rationale, monitoring, source links, and limitations; and
- schema, content, rule, source, and review metadata.

Do not infer missing values, convert ambiguous units, smooth gaps, merge conflicting ranges, or
invent an initial regimen. A band that cannot support a recommendation must explicitly represent a
`no_recommendation` outcome and reason.

### 4. Perform author verification

Before requesting independent review, the author verifies the extraction against the source:

1. Each renal band maps to at least one declared source identifier.
2. Every source identifier resolves to complete source metadata.
3. The first and last bands reproduce the declared renal domain.
4. Adjacent boundaries have exactly one owner, with no gap or overlap.
5. Dose, route, frequency, and infusion units match the supported base regimen where required.
6. Limitations capture exclusions and unresolved concerns without implying unsupported coverage.
7. Synthetic boundary and golden cases reproduce the intended source interpretation.

Author verification prepares the content for review but does not change it from `draft`.

### 5. Run schema and software verification

Run the narrowest configured checks that prove:

- the YAML parses with duplicate-key protection;
- the closed schema accepts the document;
- exact identifiers and units are preserved;
- invalid, gapped, overlapping, contradictory, or unreachable content is rejected;
- immediately-below, at, and immediately-above boundary cases behave as encoded;
- unsupported or incomplete contexts produce no recommendation;
- draft and retired content produce no recommendation; and
- successful results preserve rule ID, content version, evidence, provenance, and unrounded renal
  input.

A failing check blocks review completion and release eligibility. Do not change a test merely to
hide a content defect.

### 6. Complete independent clinical-content review

The reviewer compares the exact candidate version with the cited sources and independently checks:

- source authority, applicability, and version;
- medication and regimen identity;
- population and renal-method limits;
- renal-band values and boundary inclusivity;
- dose, route, frequency, infusion strategy, rationale, and monitoring;
- no-recommendation bands and limitations;
- source attribution for every band;
- synthetic golden cases and boundary expectations; and
- whether any ambiguity requires a narrower scope or continued draft status.

The reviewer either requests changes or approves the exact candidate. Requested clinical changes
return the document to draft and require the affected checks to be rerun. Approval is recorded by
setting status to `reviewed` and completing reviewer name, role, date, and the exact reviewed
content version.

A named independent reviewer has not yet been identified for the current prototype content. Until
that blocker is resolved, content must not be represented as independently reviewed merely because
software checks pass.

### 7. Establish prototype eligibility

A document is eligible for a prototype recommendation only when all of the following are true:

1. It remains within the chartered first-slice scope.
2. Schema validation succeeds.
3. Review status is exactly `reviewed` with complete matching metadata.
4. The exact medication, regimen, rule, and requested content version match.
5. Structural and task-sufficiency validation succeeds.
6. The context is supported and exactly one renal band matches.
7. Focused boundary, failure, golden, integration, and contract checks required for the change pass.

Eligibility is evaluated again at runtime by the rule matcher. No repository or interface may treat
“latest,” file order, directory order, or a nearby version as an implicit selection rule.

### 8. Publish and record the exact version

Reviewed content is treated as immutable for reproducible use. Record the exact content version,
source versions, rule identifier, review metadata, and relevant verification in the change record.

The schema treats `content_version` as an exact nonempty string; it does not impose semantic
versioning. Follow the repository's established identifier convention and never reuse one reviewed
version string for materially different clinical content.

Completing reviewer metadata for an unchanged draft candidate may retain that candidate's content
version. Any material clinical change after approval creates a new content version and repeats
independent review and affected verification.

## Versioning and change classification

The following changes require a new content version and renewed independent review:

- source document or source version;
- supported medication, regimen, indication, formulation, route, dose, frequency, or infusion fact;
- renal domain, band boundary, boundary inclusivity, outcome, or recommendation;
- rationale, monitoring, clinically meaningful limitation, or source-to-band mapping; and
- any correction that can change eligibility, matching, interpretation, or output.

The following changes do not by themselves redefine clinical content, but still require review of
the resulting diff and relevant checks:

- completing review metadata for an unchanged approved draft candidate;
- retirement metadata;
- nonclinical formatting that cannot alter YAML values; and
- software-only changes outside the content document.

When uncertain whether a change is clinically meaningful, treat it as material and require a new
version and review.

## Supersession

To supersede a reviewed version:

1. Create and independently review a new exact content version.
2. Verify both the new version and the intended replacement relationship.
3. Record which prior version is superseded in the change or release record.
4. Select the new version explicitly for the prototype release or test scenario.
5. Keep the prior reviewed version available only as long as an explicit rollback path is required.
6. Change the prior document to `retired` only when it must no longer be eligible for new
   evaluation.

The current schema has no `supersedes` field, and the repository has no automatic current-version
selection. Do not encode supersession by overwriting an existing reviewed document or relying on
file order.

## Rollback

Rollback restores a previously verified clinical state; it does not edit history.

1. Identify the exact prior reviewed content version and the reason for rollback.
2. Confirm that its cited sources, review metadata, tests, and software contract remain applicable.
3. Select that exact prior version explicitly in the prototype configuration or test request.
4. Rerun focused schema, boundary, failure, golden, integration, and contract checks affected by the
   rollback.
5. Record the withdrawn version, restored version, reason, reviewer, and verification results.

A `retired` document is not eligible for runtime recommendations. If the only suitable prior
version has already been retired, create a new reviewed restoration version rather than changing or
misrepresenting the retired artifact in place.

## Independent verification record

For each reviewed version, retain an auditable record containing:

- medication, regimen, content version, and rule identifier;
- source documents, versions, dates, and citations;
- author and independent reviewer identities and roles;
- review date and review outcome;
- material ambiguities, limitations, and their disposition;
- source-to-band traceability;
- independently checked boundary and golden cases;
- exact verification commands and outcomes; and
- supersession or rollback relationship when applicable.

The record may live in review metadata, repository history, and the associated change record. It
must not contain protected health information or real patient identifiers.

## Fail-closed decisions

Content remains draft or produces no recommendation when any of these conditions apply:

- no qualified independent reviewer is available;
- a source is missing, outdated without justification, conflicting, or inapplicable;
- a required source version, citation, boundary, unit, regimen fact, or limitation is absent;
- review metadata is incomplete or refers to a different content version;
- schema, boundary, golden, integration, or contract verification fails;
- the requested version is missing or does not exactly match the supplied document;
- the content is draft or retired; or
- the patient, medication, regimen, renal method, or other context is unsupported or insufficient.

Do not repair these conditions through automatic fallback, implicit “latest” selection, inference,
normalization, interpolation, or extrapolation.