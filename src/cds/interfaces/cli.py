"""Command-line interface for one synthetic renal-dose evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, TextIO, cast

from cds.mappers.renal_dose_request import (
    RenalDoseMappedInput,
    RequestMappingError,
    dto_from_mapping,
    map_renal_dose_request,
)
from cds.mappers.renal_dose_response import (
    dumps_renal_dose_response,
    map_renal_dose_response,
)
from cds.utils.serialization import JsonValue

if TYPE_CHECKING:
    from cds.app.renal_dose import RenalDoseUseCase

__all__ = ["main", "run_renal_dose_cli"]

_PROTOTYPE_DESCRIPTION = (
    "Run one prototype renal-dose evaluation using synthetic or properly de-identified JSON input. "
    "Outputs are not for direct clinical use."
)
_PROTOTYPE_SUMMARY_WARNING = (
    "PROTOTYPE — not for direct clinical use; use synthetic or properly de-identified data only."
)


def run_renal_dose_cli(
    input_path: str | Path,
    *,
    use_case: RenalDoseUseCase,
    output_path: str | Path | None = None,
    stdout: TextIO | None = None,
    summary: bool = False,
    summary_stream: TextIO | None = None,
) -> None:
    """Read, map, evaluate, and emit one canonical renal-dose JSON response.

    ``use_case`` must already be configured by the caller. The interface performs file and JSON I/O,
    delegates wire conversion to the request mapper, delegates orchestration to the application use
    case, and delegates output conversion to the canonical response mapper. It does not select
    content, validate clinical sufficiency, calculate renal function, or match rules.

    When ``summary`` is true, a presentation-only summary is written to ``summary_stream`` or
    ``stderr``. Canonical JSON remains the authoritative machine-readable output and is never mixed
    with summary text.
    """

    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    mapped = map_renal_dose_request(dto_from_mapping(payload))
    evaluation_date, evaluated_at = _required_application_times(mapped)

    result = use_case.evaluate(
        patient=mapped.patient,
        serum_creatinine_result=mapped.serum_creatinine_result,
        medication_order=mapped.medication_order,
        weight_type=mapped.weight_type,
        regimen_id=mapped.regimen_id,
        formulation_id=mapped.formulation_id,
        renal_function_stable=mapped.renal_function_stable,
        renal_replacement_therapy=mapped.renal_replacement_therapy,
        pregnant_or_lactating=mapped.pregnant_or_lactating,
        requested_content_version=mapped.requested_content_version,
        evaluation_date=evaluation_date,
        evaluated_at=evaluated_at,
    )
    response = dumps_renal_dose_response(result)

    if output_path is None:
        stream = stdout if stdout is not None else sys.stdout
        stream.write(response)
        stream.write("\n")
    else:
        Path(output_path).write_text(f"{response}\n", encoding="utf-8")

    if summary:
        stream = summary_stream if summary_stream is not None else sys.stderr
        stream.write(_format_summary(map_renal_dose_response(result)))
        stream.write("\n")


def main(
    argv: Sequence[str] | None = None,
    *,
    use_case: RenalDoseUseCase,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Parse command arguments and run one configured renal-dose use case."""

    parser = argparse.ArgumentParser(prog="cds-renal-dose", description=_PROTOTYPE_DESCRIPTION)
    parser.add_argument("input", type=Path, help="Path to one synthetic renal-dose JSON request.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path for canonical JSON output; defaults to stdout.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help=(
            "Write a concise human-readable summary to stderr; canonical JSON remains on stdout "
            "or at --output."
        ),
    )
    arguments = parser.parse_args(argv)
    run_renal_dose_cli(
        arguments.input,
        use_case=use_case,
        output_path=arguments.output,
        stdout=stdout,
        summary=arguments.summary,
        summary_stream=stderr,
    )
    return 0


def _format_summary(response: dict[str, JsonValue]) -> str:
    rule_result = _as_object(response.get("rule_result")) or {}
    status = _as_text(rule_result.get("status")) or "unknown"
    renal_text = _renal_text(rule_result)
    recommendation_texts = _recommendation_texts(rule_result)
    warning_texts = _trace_texts(response, collection_name="warnings", text_fields=("message",))
    evidence_texts = _trace_texts(
        response,
        collection_name="evidence",
        text_fields=("summary", "citation", "source_document"),
    )

    lines = [
        _PROTOTYPE_SUMMARY_WARNING,
        f"Status: {status}",
        f"Renal result: {renal_text}",
    ]
    if recommendation_texts:
        lines.append("Recommendation:")
        lines.extend(f"- {text}" for text in recommendation_texts)
    else:
        lines.append("Recommendation: not present in structured result.")

    if warning_texts:
        lines.append("Warnings:")
        lines.extend(f"- {text}" for text in warning_texts)
    else:
        lines.append("Warnings: none recorded.")

    if evidence_texts:
        lines.append("Evidence:")
        lines.extend(f"- {text}" for text in evidence_texts)
    else:
        lines.append("Evidence: none recorded.")
    return "\n".join(lines)


def _renal_text(rule_result: dict[str, JsonValue]) -> str:
    renal_result = _as_object(rule_result.get("renal_function_result"))
    if renal_result is None:
        return "not present in structured result."
    quantity = _as_object(renal_result.get("value"))
    if quantity is None:
        return "not present in structured result."
    value = _as_scalar_text(quantity.get("value"))
    unit = _as_text(quantity.get("unit"))
    if value is None:
        return "not present in structured result."
    return f"{value} {unit}" if unit else value


def _recommendation_texts(rule_result: dict[str, JsonValue]) -> list[str]:
    recommendations = _as_list(rule_result.get("recommendations")) or []
    texts: list[str] = []
    for item in recommendations:
        recommendation = _as_object(item)
        if recommendation is None:
            continue
        text = _first_text(recommendation, ("title", "summary", "rationale"))
        if text is not None and text not in texts:
            texts.append(text)
    return texts


def _trace_texts(
    response: dict[str, JsonValue],
    *,
    collection_name: str,
    text_fields: tuple[str, ...],
) -> list[str]:
    texts: list[str] = []
    rule_result = _as_object(response.get("rule_result")) or {}
    validation = _as_object(response.get("validation")) or {}
    containers = [rule_result]

    renal_result = _as_object(rule_result.get("renal_function_result"))
    if renal_result is not None:
        containers.append(renal_result)

    for recommendation_value in _as_list(rule_result.get("recommendations")) or []:
        recommendation = _as_object(recommendation_value)
        if recommendation is None:
            continue
        containers.append(recommendation)
        dose_recommendation = _as_object(recommendation.get("dose_recommendation"))
        if dose_recommendation is not None:
            containers.append(dose_recommendation)

    if collection_name == "warnings":
        warning_issues: list[JsonValue] = []
        for issue in _as_list(validation.get("issues")) or []:
            issue_object = _as_object(issue)
            if issue_object is None:
                continue
            if _as_text(issue_object.get("severity")) in {"info", "warning"}:
                warning_issues.append(issue)
        if warning_issues:
            containers.append({collection_name: warning_issues})

    for container in containers:
        for item in _as_list(container.get(collection_name)) or []:
            trace_item = _as_object(item)
            if trace_item is None:
                continue
            text = _first_text(trace_item, text_fields)
            if text is not None and text not in texts:
                texts.append(text)
    return texts


def _first_text(value: dict[str, JsonValue], fields: tuple[str, ...]) -> str | None:
    for field in fields:
        text = _as_text(value.get(field))
        if text:
            return text
    return None


def _as_object(value: JsonValue | None) -> dict[str, JsonValue] | None:
    return value if isinstance(value, dict) else None


def _as_list(value: JsonValue | None) -> list[JsonValue] | None:
    return value if isinstance(value, list) else None


def _as_text(value: JsonValue | None) -> str | None:
    return value if isinstance(value, str) and value else None


def _as_scalar_text(value: JsonValue | None) -> str | None:
    if isinstance(value, bool) or value is None or isinstance(value, (list, dict)):
        return None
    return str(value)


def _required_application_times(mapped: RenalDoseMappedInput) -> tuple[date, datetime]:
    missing_fields: list[str] = []
    if mapped.evaluation_date is None:
        missing_fields.append("evaluation_date")
    if mapped.evaluated_at is None:
        missing_fields.append("evaluated_at")
    if missing_fields:
        joined = ", ".join(repr(field) for field in missing_fields)
        raise RequestMappingError(
            f"Request field(s) {joined} must be supplied before use-case invocation."
        )
    return cast(date, mapped.evaluation_date), cast(datetime, mapped.evaluated_at)
