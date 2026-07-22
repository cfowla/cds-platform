"""Passive validation issue and result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

ValidationSeverity: TypeAlias = Literal["error", "warning", "unknown"]

__all__ = ["ValidationIssue", "ValidationResult", "ValidationSeverity"]


@dataclass(slots=True, kw_only=True)
class ValidationIssue:
    """Carry one validation finding without performing validation.

    Missing issue details remain ``None`` and severity remains ``"unknown"`` until a validator
    assigns them. ``field_path`` may identify the relevant input without coupling this passive
    model to a specific DTO, domain model, or interface.
    """

    code: str | None = None
    message: str | None = None
    severity: ValidationSeverity = "unknown"
    field_path: str | None = None


@dataclass(slots=True, kw_only=True)
class ValidationResult:
    """Carry validation status and findings without deriving either value.

    ``is_valid=None`` represents an unevaluated or indeterminate state and remains distinct from
    explicit valid and invalid results. Validators are responsible for assigning status and
    populating issues before calculation or rule matching occurs.
    """

    is_valid: bool | None = None
    issues: list[ValidationIssue] = field(default_factory=list)
