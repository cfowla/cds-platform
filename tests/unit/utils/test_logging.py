"""Focused tests for the privacy-preserving logging policy."""

from __future__ import annotations

import logging

import pytest

from cds.utils.logging import SafeDiagnosticEvent, log_diagnostic, log_failure

_LOGGER_NAME = "tests.cds.safe_logging"


def test_diagnostic_emits_only_allowlisted_controlled_fields(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger(_LOGGER_NAME)

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        log_diagnostic(
            logger,
            logging.INFO,
            event="request.rejected",
            component="cli",
            operation="renal_dose_evaluation",
            stage="request_mapping",
            status="incomplete",
            failure_code="invalid_input",
        )

    assert caplog.messages == [
        "event=request.rejected component=cli operation=renal_dose_evaluation "
        "stage=request_mapping status=incomplete failure_code=invalid_input"
    ]
    record = caplog.records[0]
    assert record.cds_event == "request.rejected"
    assert record.cds_component == "cli"
    assert record.exc_info is None


def test_failure_excludes_exception_message_payload_and_traceback(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger(_LOGGER_NAME)
    synthetic_patient_id = "synthetic-patient-logging-001"
    synthetic_payload = '{"serum_creatinine_value":"9.99"}'
    exception = RuntimeError(
        f"patient_id={synthetic_patient_id} payload={synthetic_payload}"
    )

    with caplog.at_level(logging.ERROR, logger=_LOGGER_NAME):
        log_failure(
            logger,
            event="evaluation.failed",
            component="app",
            operation="renal_dose_evaluation",
            stage="renal_calculation",
            failure_code="unexpected_failure",
            exception=exception,
        )

    assert caplog.messages == [
        "event=evaluation.failed component=app operation=renal_dose_evaluation "
        "stage=renal_calculation status=failed failure_code=unexpected_failure "
        "exception_type=RuntimeError"
    ]
    assert synthetic_patient_id not in caplog.text
    assert synthetic_payload not in caplog.text
    assert str(exception) not in caplog.text
    assert "Traceback" not in caplog.text
    assert caplog.records[0].exc_info is None


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("event", "request rejected: patient_id=synthetic-patient-001"),
        ("component", '{"payload":"synthetic-case-detail"}'),
        ("stage", "request mapping"),
        ("failure_code", "InvalidInput"),
    ],
)
def test_free_text_and_payload_like_diagnostic_values_are_rejected(
    field_name: str,
    value: str,
) -> None:
    kwargs = {
        "event": "request.rejected",
        "component": "cli",
        "stage": "request_mapping",
        "failure_code": "invalid_input",
    }
    kwargs[field_name] = value

    with pytest.raises(ValueError, match="controlled diagnostic token"):
        SafeDiagnosticEvent(**kwargs)


def test_public_diagnostic_helper_does_not_accept_patient_or_payload_fields() -> None:
    logger = logging.getLogger(_LOGGER_NAME)

    with pytest.raises(TypeError):
        log_diagnostic(
            logger,
            logging.INFO,
            event="request.received",
            component="cli",
            patient_id="synthetic-patient-001",  # type: ignore[call-arg]
        )

    with pytest.raises(TypeError):
        log_diagnostic(
            logger,
            logging.INFO,
            event="request.received",
            component="cli",
            payload={"synthetic": "case"},  # type: ignore[call-arg]
        )
