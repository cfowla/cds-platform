"""Shared pure matcher for one exact renal-dose regimen and reviewed content document."""

from __future__ import annotations

from dataclasses import dataclass
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

_OUTCOME_CATEGORY_KEY = "outcome_category"
_OUTCOME_INCOMPLETE = "incomplete"
_OUTCOME_UNSUPPORTED = "unsupported"
_OUTCOME_NOT_APPLICABLE = "not_applicable"
_OUTCOME_RECOMMENDATION = "recommendation"


@dataclass(frozen=True, slots=True)
class ExactRenalDoseRuleConfig:
    """Medication-specific labels and identifiers for the shared exact matcher."""

    medication_id: str
    medication_display: str
    implementation_version: str
    warning_code_prefix: str
    recommendation_title: str
    provenance_source_name: str
    minimum_weight: RenalDoseQuantity | None = None


__all__ = ["ExactRenalDoseRuleConfig", "evaluate_exact_renal_dose_rule"]


def evaluate_exact_renal_dose_rule(
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
    config: ExactRenalDoseRuleConfig,
) -> RuleResult:
    """Evaluate an exact validated order against one reviewed immutable content document.

    This function performs no I/O, content selection, identifier normalization, quantity conversion,
    rounding, or clinical inference. Missing facts remain incomplete. Nonmatching supported-context
    facts are explicit unsupported outcomes. Every fail-closed outcome contains no dose
    recommendation.
    """

    result = _base_result(
        order=order,
        renal_function=renal_function,
        content=content,
        requested_content_version=requested_content_version,
        evaluated_at=evaluated_at,
        config=config,
    )

    if not _review_is_eligible(content):
        return _incomplete(
            result,
            f"{config.medication_display} content is not independently reviewed and eligible.",
        )

    if requested_content_version is None:
        return _incomplete(result, "Required content version is missing.")
    if requested_content_version != content.content_version:
        return _incomplete(
            result,
            "Requested content version does not exactly match the supplied content.",
        )

    if content.medication.id != config.medication_id:
        return _incomplete(
            result,
            f"Supplied content is not exact {config.medication_display} content.",
        )

    if order.order_id is None or order.patient_id is None:
        return _incomplete(result, "Required medication-order identity is missing.")

    if renal_function.patient_id is None or renal_function.patient_id != order.patient_id:
        return _incomplete(
            result,
            "Renal result and medication order do not identify the same patient.",
        )

    if (
        order.encounter_id is not None
        and renal_function.encounter_id is not None
        and order.encounter_id != renal_function.encounter_id
    ):
        return _incomplete(
            result,
            "Renal result and medication order identify different encounters.",
        )

    if order.medication.code is None:
        return _incomplete(result, "Medication identifier is missing.")
    if order.medication.code != config.medication_id:
        return _not_applicable(
            result,
            f"The {config.medication_display} rule does not apply to this medication order.",
        )

    if regimen_id is None:
        return _incomplete(
            result,
            f"Required {config.medication_display} regimen identifier is missing.",
        )
    if regimen_id != content.regimen.id:
        return _unsupported(
            result,
            f"{config.medication_display} regimen identifier is not supported by the "
            "supplied reviewed content.",
            code=_warning_code(config, "regimen"),
            config=config,
        )

    if order.indication.code is None:
        return _incomplete(
            result,
            f"Required {config.medication_display} indication identifier is missing.",
        )
    if order.indication.code not in content.regimen.indication_ids:
        return _unsupported(
            result,
            f"{config.medication_display} indication is outside the supplied reviewed "
            "regimen context.",
            code=_warning_code(config, "indication"),
            config=config,
        )

    if order.route.code is None:
        return _incomplete(
            result,
            f"Required {config.medication_display} route identifier is missing.",
        )
    if order.route.code != content.regimen.route_id:
        return _unsupported(
            result,
            f"{config.medication_display} route is outside the supplied reviewed regimen context.",
            code=_warning_code(config, "route"),
            config=config,
        )

    if formulation_id is None and content.regimen.formulation_id is not None:
        return _incomplete(
            result,
            f"Required {config.medication_display} formulation identifier is missing.",
        )
    if formulation_id != content.regimen.formulation_id:
        return _unsupported(
            result,
            f"{config.medication_display} formulation is outside the supplied reviewed "
            "regimen context.",
            code=_warning_code(config, "formulation"),
            config=config,
        )

    if _quantity_is_missing(order.dose, content.regimen.base_dose):
        return _incomplete(
            result,
            f"Required {config.medication_display} dose value or unit is missing.",
        )
    if not _quantity_matches(order.dose, content.regimen.base_dose):
        return _unsupported(
            result,
            f"{config.medication_display} dose value or unit is outside the supplied "
            "reviewed regimen context.",
            code=_warning_code(config, "dose"),
            config=config,
        )

    if _quantity_is_missing(order.frequency_interval, content.regimen.frequency_interval):
        return _incomplete(
            result,
            f"Required {config.medication_display} frequency interval or unit is missing.",
        )
    if not _quantity_matches(order.frequency_interval, content.regimen.frequency_interval):
        return _unsupported(
            result,
            f"{config.medication_display} frequency is outside the supplied reviewed "
            "regimen context.",
            code=_warning_code(config, "frequency"),
            config=config,
        )

    if _quantity_is_missing(order.infusion_duration, content.regimen.infusion_duration):
        return _incomplete(
            result,
            f"Required {config.medication_display} infusion duration or unit is missing.",
        )
    if not _quantity_matches(order.infusion_duration, content.regimen.infusion_duration):
        return _unsupported(
            result,
            f"{config.medication_display} infusion strategy is outside the supplied "
            "reviewed regimen context.",
            code=_warning_code(config, "infusion"),
            config=config,
        )

    renal_value = renal_function.value.value
    supported_context = content.supported_context

    if renal_function.age_years is None:
        return _incomplete(result, "Required patient age is missing.")
    if renal_function.age_years < supported_context.minimum_age_years:
        return _unsupported(
            result,
            f"Pediatric {config.medication_display} dosing is outside the reviewed adult "
            "content context.",
            code=_warning_code(config, "population"),
            config=config,
        )

    if config.minimum_weight is not None:
        if _quantity_is_missing(renal_function.weight_used, config.minimum_weight):
            return _incomplete(result, "Required patient weight or unit is missing.")
        if renal_function.weight_used.unit != config.minimum_weight.unit:
            return _unsupported(
                result,
                f"Patient weight unit is outside the reviewed {config.medication_display} "
                "content context.",
                code=_warning_code(config, "population"),
                config=config,
            )
        if renal_function.weight_used.value < config.minimum_weight.value:
            return _unsupported(
                result,
                f"Patients weighing less than {config.minimum_weight.value} "
                f"{config.minimum_weight.unit} are outside the reviewed "
                f"{config.medication_display} adult content context.",
                code=_warning_code(config, "population"),
                config=config,
            )

    if renal_function.method is RenalMethod.UNKNOWN:
        return _incomplete(result, "Required renal method is missing or unknown.")
    if renal_function.method.value != supported_context.renal_method:
        return _unsupported(
            result,
            "Renal method is outside the supplied reviewed "
            f"{config.medication_display} content context.",
            code=_warning_code(config, "renal_method"),
            config=config,
        )

    if renal_value is None or renal_function.value.unit is None:
        return _incomplete(result, "Required renal value or unit is missing.")
    if renal_function.value.unit != supported_context.renal_unit:
        return _unsupported(
            result,
            "Renal unit is outside the supplied reviewed "
            f"{config.medication_display} content context.",
            code=_warning_code(config, "renal_unit"),
            config=config,
        )

    if renal_function.normalized_to_bsa is None:
        return _incomplete(result, "Renal indexing status is missing.")
    if renal_function.normalized_to_bsa is not False:
        return _unsupported(
            result,
            "Indexed renal results are outside the supplied reviewed content context.",
            code="unsupported_indexed_renal_result",
            config=config,
        )

    if renal_function_stable is None:
        return _incomplete(result, "Renal-stability context is missing.")
    if renal_function_stable is not supported_context.renal_function_stable:
        return _unsupported(
            result,
            "Unstable renal function is outside the supplied reviewed content context.",
            code="unsupported_unstable_renal_function",
            config=config,
        )

    if renal_replacement_therapy is None:
        return _incomplete(result, "Renal-replacement-therapy context is missing.")
    if renal_replacement_therapy is not supported_context.renal_replacement_therapy:
        return _unsupported(
            result,
            "Renal replacement therapy is outside the supplied reviewed content context.",
            code="unsupported_renal_replacement_therapy",
            config=config,
        )

    if not renal_band_matches(
        renal_value,
        lower=content.renal_domain.lower,
        upper=content.renal_domain.upper,
    ):
        return _unsupported(
            result,
            "Renal value is outside the reviewed content domain; no extrapolation was performed.",
            code=_warning_code(config, "renal_domain"),
            config=config,
        )

    matching_bands = [
        band
        for band in content.renal_bands
        if renal_band_matches(renal_value, lower=band.lower, upper=band.upper)
    ]
    if len(matching_bands) != 1:
        return _incomplete(
            result,
            "Renal content produced zero or multiple exact band matches.",
        )

    band = matching_bands[0]
    if band.outcome != "recommendation" or band.recommendation is None:
        return _no_recommendation_result(result, band, config=config)

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
            result,
            "Matched content lacks a complete structured dose recommendation.",
        )

    evidence = _band_evidence(content, band)
    if evidence is None:
        return _incomplete(result, "Matched renal band references missing evidence content.")

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
        title=config.recommendation_title,
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

    result.status = ResultStatus.SUCCESS
    result.applied = True
    result.passed = True
    result.summary = (
        f"Exact reviewed {config.medication_display} content matched one renal band."
    )
    result.recommendations = [recommendation]
    result.evidence = list(evidence)
    result.provenance = provenance
    result.supporting_data.update(
        {
            _OUTCOME_CATEGORY_KEY: _OUTCOME_RECOMMENDATION,
            "renal_band_id": band.id,
            "renal_value": str(renal_value),
            "renal_unit": renal_function.value.unit,
        }
    )
    return result


def _base_result(
    *,
    order: MedicationOrder,
    renal_function: RenalFunctionResult,
    content: RenalDoseContent,
    requested_content_version: str | None,
    evaluated_at: datetime,
    config: ExactRenalDoseRuleConfig,
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
            "rule_implementation_version": config.implementation_version,
        },
    )


def _incomplete(result: RuleResult, summary: str) -> RuleResult:
    result.status = ResultStatus.INCOMPLETE
    result.applied = False
    result.passed = None
    result.summary = summary
    result.supporting_data[_OUTCOME_CATEGORY_KEY] = _OUTCOME_INCOMPLETE
    result.recommendations = []
    result.warnings = []
    return result


def _unsupported(
    result: RuleResult,
    summary: str,
    *,
    code: str,
    config: ExactRenalDoseRuleConfig,
) -> RuleResult:
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
            provenance=_result_provenance(result, config=config),
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
    result.warnings = []
    return result


def _no_recommendation_result(
    result: RuleResult,
    band: RenalDoseBandContent,
    *,
    config: ExactRenalDoseRuleConfig,
) -> RuleResult:
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
            code=f"{config.warning_code_prefix}_no_recommendation_band",
            message=summary,
            severity="warning",
            provenance=_result_provenance(result, config=config),
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


def _warning_code(config: ExactRenalDoseRuleConfig, suffix: str) -> str:
    return f"unsupported_{config.warning_code_prefix}_{suffix}"


def _content_provenance(content: RenalDoseContent, evaluated_at: datetime) -> Provenance:
    return Provenance(
        source_type="rule_content",
        source_name="renal_dose_content",
        source_identifier=content.content_id,
        captured_at=evaluated_at,
        version=content.content_version,
    )


def _result_provenance(
    result: RuleResult,
    *,
    config: ExactRenalDoseRuleConfig,
) -> Provenance:
    content_version = result.supporting_data.get("content_version")
    return Provenance(
        source_type="rule_content",
        source_name=config.provenance_source_name,
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
