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
from cds.mappers.renal_dose_response import dumps_renal_dose_response

if TYPE_CHECKING:
    from cds.app.renal_dose import RenalDoseUseCase

__all__ = ["main", "run_renal_dose_cli"]

_PROTOTYPE_DESCRIPTION = (
    "Run one prototype renal-dose evaluation using synthetic or properly de-identified JSON input. "
    "Outputs are not for direct clinical use."
)


def run_renal_dose_cli(
    input_path: str | Path,
    *,
    use_case: RenalDoseUseCase,
    output_path: str | Path | None = None,
    stdout: TextIO | None = None,
) -> None:
    """Read, map, evaluate, and emit one canonical renal-dose JSON response.

    ``use_case`` must already be configured by the caller. The interface performs file and JSON I/O,
    delegates wire conversion to the request mapper, delegates orchestration to the application use
    case, and delegates output conversion to the canonical response mapper. It does not select
    content, validate clinical sufficiency, calculate renal function, or match rules.
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
        return

    Path(output_path).write_text(f"{response}\n", encoding="utf-8")


def main(
    argv: Sequence[str] | None = None,
    *,
    use_case: RenalDoseUseCase,
    stdout: TextIO | None = None,
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
    arguments = parser.parse_args(argv)
    run_renal_dose_cli(
        arguments.input,
        use_case=use_case,
        output_path=arguments.output,
        stdout=stdout,
    )
    return 0


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
