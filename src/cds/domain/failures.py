"""Passive, sanitized failure details for application-owned results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

FailureCategory: TypeAlias = Literal[
    "validation_error",
    "unsupported_context",
    "content_not_found",
    "content_integrity_error",
    "calculation_error",
    "rule_evaluation_error",
    "mapping_error",
    "system_failure",
    "unknown",
]

__all__ = ["FailureCategory", "FailureDetail"]


@dataclass(frozen=True, slots=True, kw_only=True)
class FailureDetail:
    """Carry an externally safe failure classification without exception text or traceback data."""

    category: FailureCategory = "unknown"
    code: str | None = None
    stage: str | None = None
    summary: str | None = None
    retryable: bool | None = None
