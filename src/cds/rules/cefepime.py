"""Pure exact-context cefepime renal-dose rule evaluation."""

from __future__ import annotations

from datetime import datetime

from cds.domain.clinical import MedicationOrder
from cds.domain.enums import RenalMethod, ResultStatus
from cds.domain.outputs import (
    CDSRecommendation,
    DoseRecommendation,
    RenalFunctionResult,
    RuleResult,
)
from cds.domain.support import EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.repositories.renal_content import (
    RenalDoseBandContent,
    RenalDoseContent,
    RenalDoseQuantity,
    RenalDoseSourceContent,
)
from cds.rules.predicates import renal_band_matches

CEFEPIME_MEDICATION_ID = "cefepime"
CEFEPIME_RULE_IMPLEMENTATION_VERSION = "1.1.0"

_OUTCOME_CATEGORY_KEY = "outcome_category"
_OUTCOME_INCOMPLETE = "incomplete"
_OUTCOME_UNSUPPORTED = "unsupported"
_OUTCOME_NOT_APPLICABLE = "not_applicable"
_OUTCOME_RECOMMENDATION = "recommendation"

__all__ = [
    "CEFEPIME_MEDICATION_ID",
    "CEFEPIME_RULE_IMPLEMENTATION_VERSION",
    "evaluate_cefepime_rule",
]


def evaluate_cefepime_rule(
    *,
    order: MedicationOrder,
    renal_function: RenalFunctionResult,
    regimen_id: str | None,
    formulation_id: str | None,
    renal_function_stable: bool | None,
    renal_replacement_therapy: bool | None,
    requested_content_version: str | None,
    content: RenalDoseContent,
    evaluated_at: datetime,
) -> RuleResult:
    """Evaluate one exact cefepime regimen against one reviewed immutable content document.

    Inputs are expected to have completed structural and task-sufficiency validation. This rule
    still fails closed when required facts are absent or do not exactly match the supplied content.
    It does not load content, select a version, normalize identifiers or units, convert quantities,
    round the renal value, infer missing context, or extrapolate beyond reviewed content.
    """

    base_result = _base_result(
        order=order,
        renal_function=renal_function,
        content=content,
        requested_content_version=requested_content_version,
        evaluated_at=evaluated_at,
    )

    if not _review_is_eligible(content):
        return _incomplete(
            base_result,
            "Cefepime content is not independently reviewed and eligible.",
        )

    if requested_content_version is None:
        return _incomplete(base_result, "Required content version is missing.")
    if requested_content_version != content.content_version:
        return _incomplete(
            base_result,
            "Requested content version does not exactly match the supplied content.",
        )

    if content.medication.id != CEFEPIME_MEDICATION_ID:
        return _incomplete(base_result, "Supplied content is not exact cefepime content.")

    if order.order_id is None or order.patient_id is None:
        return _incomplete(base_result, "Required medication-order identity is missing.")

    if renal_function.patient_id is None or renal_function.patient_id != order.patient_id:
        return _incomplete(
            base_result,
            "Renal result and medication order do not identify the same patient.",
        )

    if (
        order.encounter_id is not None
        and renal_function.encounter_id is not None
        and order.encounter_id != renal_function.encounter_id
    ):
        return _incomplete(
            base_result,
            "Renal result and medication order identify different encounters.",
        )

    if order.medication.code is None:
        return _incomplete(base_result, "Medication identifier is missing.")
    if order.medication.code != CEFEPIME_MEDICATION_ID:
        return _not_applicable(
            base_result,
            "The cefepime rule does not apply to a non-cefepime medication order.",
        )

    if regimen_id is None:
        return _incomplete(base_result, "Required cefepime regimen identifier is missing.")
    if regimen_id != content.regimen.id:
        return _unsupported(
            base_result,
            "Cefepime regimen identifier is not supported by the supplied reviewed content.",
            code="unsupported_cefepime_regimen",
        )

    if order.indication.code is None:
        return _incomplete(base_result, "Required cefepime indication identifier is missing.")
    if order.indication.code not in content.regimen.indication_ids:
        return _unsupported(
            base_result,
            "Cefepime indication is outside the supplied reviewed regimen context.",
            code="unsupported_cefepime_indication",
        )

    if order.route.code is None:
        return _incomplete(base_result, "Required cefepime route identifier is missing.")
    if order.route.code != content.regimen.route_id:
        return _unsupported(
            base_result,
            "Cefepime route is outside the supplied reviewed regimen context.",
            code="unsupported_cefepime_route",
        )

    if formulation_id is None and content.regimen.formulation_id is not None:
        return _incomplete(base_result, "Required cefepime formulation identifier is missing.")
    if formulation_id != content.regimen.formulation_id:
        return _unsupported(
            base_result,
            "Cefepime formulation is outside the supplied reviewed regimen context.",
            code="unsupported_cefepime_formulation",
        )

    if _quantity_is_missing(order.dose, content.regimen.base_dose):
        return _incomplete(base_result, "Required cefepime dose value or unit is missing.")
    if not _quantity_matches(order.dose, content.regimen.base_dose):
        return _unsupported(
            base_result,
            "Cefepime dose value or unit is outside the supplied reviewed regimen context.",
            code="unsupported_cefepime_dose",
        )

    if _quantity_is_missing(order.frequency_interval, content.regimen.frequency_interval):
        return _incomplete(base_result, "Required cefepime frequency interval or unit is missing.")
    if not _quantity_matches(order.frequency_interval, content.regimen.frequency_interval):
        return _unsupported(
            base_result,
            "Cefepime frequency is outside the supplied reviewed regimen context.",
            code="unsupported_cefepime_frequency",
        )

    if _quantity_is_missing(order.infusion_duration, content.regimen.infusion_duration):
        return _incomplete(base_result, "Required cefepime infusion duration or unit is missing.")
    if not _quantity_matches(order.infusion_duration, content.regimen.infusion_duration):
        return _unsupported(
            base_result,
            "Cefepime infusion strategy is outside the supplied reviewed regimen context.",
            code="unsupported_cefepime_infusion",
        )

    renal_value = renal_function.value.value
    supported_context = content.supported_context
    if renal_function.age_years is None:
        return _incomplete(base_result, "Required patient age is missing.")
    if renal_function.age_years < supported_context.minimum_age_years:
        return _unsupported(
            base_result,
            "Pediatric cefepime dosing is outside the reviewed adult content context.",
            code="unsupported_cefepime_population",
        )

    if renal_function.method is RenalMethod.UNKNOWN:
        return _incomplete(base_result, "Required renal method is missing or unknown.")
    if renal_function.method.value != supported_context.renal_method:
        return _unsupported(
            base_result,
            "Renal method is outside the supplied reviewed cefepime content context.",
            code="unsupported_cefepime_renal_method",
        )

    if renal_value is None or renal_function.value.unit is None:
        return _incomplete(base_result, "Required renal value or unit is missing.")
    if renal_function.value.unit != supported_context.renal_unit:
        return _unsupported(
            base_result,
            "Renal unit is outside the supplied reviewed cefepime content context.",
            code="unsupported_cefepime_renal_unit",
        )

    if renal_function.normalized_to_bsa is None:
        return _incomplete(base_result, "Renal indexing status is missing.")
    if renal_function.normalized_to_bsa is not False:
        return _unsupported(
            base_result,
            "Indexed renal results are outside the supplied reviewed cefepime content context.",
            code="unsupported_indexed_renal_result",
        )

    if renal_function_stable is None:
        return _incomplete(base_result, "Renal-stability context is missing.")
    if renal_function_stable is not supported_context.renal_function_stable:
        return _unsupported(
            base_result,
            "Unstable renal function is outside the supplied reviewed cefepime content context.",
            code="unsupported_unstable_renal_function",
        )

    if renal_replacement_therapy is None:
        return _incomplete(base_result, "Renal-replacement-therapy context is missing.")
    if renal_replacement_therapy is not supported_context.renal_replacement_therapy:
        return _unsupported(
            base_result,
            "Renal replacement therapy is outside the supplied reviewed cefepime content context.",
            code="unsupported_renal_replacement_therapy",
        )

    if not renal_band_matches(
        renal_value,
        lower=content.renal_domain.lower,
        upper=content.renal_domain.upper,
    ):
        return _unsupported(
            base_result,
            "Renal value is outside the reviewed content domain; no extrapolation was performed.",
            code="unsupported_cefepime_renal_domain",
        )

    matching_bands = [
        band
        for band in content.renal_bands
        if renal_band_matches(renal_value, lower=band.lower, upper=band.upper)
    ]
    if len(matching_bands) != 1:
        return _incomplete(
            base_result,
            "Renal content produced zero or multiple exact band matches.",
        )

    band = matching_bands[0]
    if band.outcome != "recommendation" or band.recommendation is None:
        return _no_recommendation_result(base_result, band)

    recommendation_content = band.recommendation
    if (
        recommendation_content.dose is None
        or recommendation_content.route_id is None
        or recommendation_content.frequency_interval is None
        or (
            content.regimen.infusion_duration is not None
            and recommendation_content.infusion_duration is None
        )
    ):
        return _incomplete(
            base_result,
            "Matched content lacks a complete structured dose recommendation.",
        )

    evidence = _band_evidence(content, band)
    if evidence is None:
        return _incomplete(base_result, "Matched renal band references missing evidence content.")

    provenance = _content_provenance(content, evaluated_at)
    dose_recommendation = DoseRecommendation(
        medication=CodeableConcept(text=content.medication.display, code=content.medication.id),
        recommended_dose=_as_value_with_unit(recommendation_content.dose),
        recommended_route=CodeableConcept(code=recommendation_content.route_id),
        frequency_interval=_as_value_with_unit(recommendation_content.frequency_interval),
        infusion_duration=_as_value_with_unit(recommendation_content.infusion_duration),
        regimen_variant=content.regimen.id,
        rationale=recommendation_content.rationale,
        evidence=list(evidence),
        provenance=provenance,
    )
    recommendation = CDSRecommendation(
        recommendation_id=f"{content.rule_id}:{band.id}:{order.order_id}",
        patient_id=order.patient_id,
        encounter_id=order.encounter_id,
        title="Cefepime renal-dose recommendation",
        action=recommendation_content.action,
        strength="recommend",
        summary=recommendation_content.rationale,
        rationale=recommendation_content.rationale,
        renal_function_result=renal_function,
        dose_recommendation=dose_recommendation,
        suggested_monitoring=list(recommendation_content.monitoring),
        linked_order_id=order.order_id,
        linked_rule_id=content.rule_id,
        evidence=list(evidence),
        provenance=provenance,
    )

    base_result.status = ResultStatus.SUCCESS
    base_result.applied = True
    base_result.passed = True
    base_result.summary = "Exact reviewed cefepime content matched one renal band."
    base_result.recommendations = [recommendation]
    base_result.evidence = list(evidence)
    base_result.provenance = provenance
    base_result.supporting_data.update(
        {
            _OUTCOME_CATEGORY_KEY: _OUTCOME_RECOMMENDATION,
            "renal_band_id": band.id,
            "renal_value": str(renal_value),
            "renal_unit": renal_function.value.unit,
        }
    )
    return base_result


def _base_result(
    *,
    order: MedicationOrder,
    renal_function: RenalFunctionResult,
    content: RenalDoseContent,
    requested_content_version: str | None,
    evaluated_at: datetime,
) -> RuleResult:
    return RuleResult(
        rule_id=content.rule_id,
        patient_id=order.patient_id,
        encounter_id=order.encounter_id,
        status=ResultStatus.INCOMPLETE,
        applied=False,
        passed=None,
        renal_function_result=renal_function,
        evaluated_at=evaluated_at,
        supporting_data={
            "medication_id": order.medication.code,
            "content_medication_id": content.medication.id,
            "regimen_id": content.regimen.id,
            "requested_content_version": requested_content_version,
            "content_version": content.content_version,
            "rule_implementation_version": CEFEPIME_RULE_IMPLEMENTATION_VERSION,
        },
    )


def _incomplete(result: RuleResult, summary: str) -> RuleResult:
    result.status = ResultStatus.INCOMPLETE
    result.applied = False
    result.passed = None
    result.summary = summary
    result.supporting_data[_OUTCOME_CATEGORY_KEY] = _OUTCOME_INCOMPLETE
    result.recommendations = []
    return result


def _unsupported(result: RuleResult, summary: str, *, code: str) -> RuleResult:
    result.status = ResultStatus.NOT_APPLICABLE
    result.applied = False
    result.passed = None
    result.summary = summary
    result.supporting_data[_OUTCOME_CATEGORY_KEY] = _OUTCOME_UNSUPPORTED
    result.recommendations = []
    result.warnings = [
        WarningNote(
            code=code,
            message=summary,
            severity="warning",
            provenance=_result_provenance(result),
        )
    ]
    return result


def _not_applicable(result: RuleResult, summary: str) -> RuleResult:
    result.status = ResultStatus.NOT_APPLICABLE
    result.applied = False
    result.passed = None
    result.summary = summary
    result.supporting_data[_OUTCOME_CATEGORY_KEY] = _OUTCOME_NOT_APPLICABLE
    result.recommendations = []
    return result


def _no_recommendation_result(result: RuleResult, band: RenalDoseBandContent) -> RuleResult:
    summary = band.no_recommendation_reason or "Matched content permits no dose recommendation."
    result.status = ResultStatus.NOT_APPLICABLE
    result.applied = True
    result.passed = False
    result.summary = summary
    result.supporting_data[_OUTCOME_CATEGORY_KEY] = _OUTCOME_NOT_APPLICABLE
    result.supporting_data["renal_band_id"] = band.id
    result.recommendations = []
    result.warnings = [
        WarningNote(
            code="cefepime_no_recommendation_band",
            message=summary,
            severity="warning",
            provenance=_result_provenance(result),
        )
    ]
    return result


def _review_is_eligible(content: RenalDoseContent) -> bool:
    review = content.review
    return (
        review.status == "reviewed"
        and review.reviewed_content_version == content.content_version
        and bool(review.reviewer)
        and bool(review.reviewer_role)
        and review.reviewed_on is not None
    )


def _quantity_is_missing(actual: ValueWithUnit, expected: RenalDoseQuantity | None) -> bool:
    if expected is None:
        return False
    return actual.value is None or actual.unit is None


def _quantity_matches(actual: ValueWithUnit, expected: RenalDoseQuantity | None) -> bool:
    if expected is None:
        return actual.value is None and actual.unit is None
    return actual.value == expected.value and actual.unit == expected.unit


def _as_value_with_unit(quantity: RenalDoseQuantity | None) -> ValueWithUnit:
    if quantity is None:
        return ValueWithUnit()
    return ValueWithUnit(value=quantity.value, unit=quantity.unit)


def _content_provenance(content: RenalDoseContent, evaluated_at: datetime) -> Provenance:
    return Provenance(
        source_type="rule_content",
        source_name="renal_dose_content",
        source_identifier=content.content_id,
        captured_at=evaluated_at,
        version=content.content_version,
    )


def _result_provenance(result: RuleResult) -> Provenance:
    content_version = result.supporting_data.get("content_version")
    return Provenance(
        source_type="rule_content",
        source_name="cefepime_rule",
        source_identifier=result.rule_id,
        captured_at=result.evaluated_at,
        version=content_version if isinstance(content_version, str) else None,
    )


def _band_evidence(
    content: RenalDoseContent,
    band: RenalDoseBandContent,
) -> tuple[EvidenceItem, ...] | None:
    sources_by_id: dict[str, RenalDoseSourceContent] = {
        source.id: source for source in content.sources
    }
    if not band.source_ids or any(source_id not in sources_by_id for source_id in band.source_ids):
        return None

    return tuple(
        EvidenceItem(
            summary=f"Source supporting renal band {band.id}.",
            level=source.evidence_level,
            citation=source.citation,
            url=source.url,
            source_document=source.source_document,
            source_version=source.source_version,
            provenance=Provenance(
                source_type="rule_content",
                source_name="renal_dose_content_source",
                source_identifier=source.id,
                version=content.content_version,
            ),
        )
        for source_id in band.source_ids
        for source in (sources_by_id[source_id],)
    )