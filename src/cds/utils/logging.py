"""Privacy-preserving diagnostic logging for the CDS prototype.

The public helpers accept only controlled diagnostic codes. They intentionally do not accept
patient identifiers, request or response payloads, arbitrary metadata, exception messages, or
tracebacks. Structured clinical results remain the appropriate boundary for clinician-facing
warnings, evidence, and provenance.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

__all__ = [
    "SafeDiagnosticEvent",
    "log_diagnostic",
    "log_failure",
]

_SAFE_TOKEN_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
_SAFE_EXCEPTION_TYPE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]{0,127}$")


@dataclass(frozen=True, slots=True)
class SafeDiagnosticEvent:
    """One allowlisted diagnostic event containing no clinical or patient data."""

    event: str
    component: str
    operation: str | None = None
    stage: str | None = None
    status: str | None = None
    failure_code: str | None = None
    exception_type: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "event",
            "component",
            "operation",
            "stage",
            "status",
            "failure_code",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _validate_safe_token(field_name, value)
        if self.exception_type is not None:
            _validate_exception_type(self.exception_type)

    def as_log_message(self) -> str:
        """Return a stable key-value message made only from allowlisted fields."""

        pairs = [f"event={self.event}", f"component={self.component}"]
        for field_name in (
            "operation",
            "stage",
            "status",
            "failure_code",
            "exception_type",
        ):
            value = getattr(self, field_name)
            if value is not None:
                pairs.append(f"{field_name}={value}")
        return " ".join(pairs)

    def as_log_extra(self) -> dict[str, str]:
        """Return safe structured fields for logging formatters and handlers."""

        extra = {
            "cds_event": self.event,
            "cds_component": self.component,
        }
        for field_name in (
            "operation",
            "stage",
            "status",
            "failure_code",
            "exception_type",
        ):
            value = getattr(self, field_name)
            if value is not None:
                extra[f"cds_{field_name}"] = value
        return extra


def log_diagnostic(
    logger: logging.Logger,
    level: int,
    *,
    event: str,
    component: str,
    operation: str | None = None,
    stage: str | None = None,
    status: str | None = None,
    failure_code: str | None = None,
) -> None:
    """Log controlled diagnostic codes without accepting free text or payload data."""

    diagnostic = SafeDiagnosticEvent(
        event=event,
        component=component,
        operation=operation,
        stage=stage,
        status=status,
        failure_code=failure_code,
    )
    _emit(logger, level, diagnostic)


def log_failure(
    logger: logging.Logger,
    *,
    event: str,
    component: str,
    stage: str,
    failure_code: str,
    exception: BaseException,
    operation: str | None = None,
    level: int = logging.ERROR,
) -> None:
    """Log an exception class without its message, arguments, payload, or traceback."""

    diagnostic = SafeDiagnosticEvent(
        event=event,
        component=component,
        operation=operation,
        stage=stage,
        status="failed",
        failure_code=failure_code,
        exception_type=type(exception).__name__,
    )
    _emit(logger, level, diagnostic)


def _emit(logger: logging.Logger, level: int, diagnostic: SafeDiagnosticEvent) -> None:
    logger.log(
        level,
        "%s",
        diagnostic.as_log_message(),
        extra=diagnostic.as_log_extra(),
    )


def _validate_safe_token(field_name: str, value: str) -> None:
    if not _SAFE_TOKEN_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} must be a lower-case controlled diagnostic token, not free text"
        )


def _validate_exception_type(value: str) -> None:
    if not _SAFE_EXCEPTION_TYPE_PATTERN.fullmatch(value):
        raise ValueError("exception_type must be a Python exception class name")
